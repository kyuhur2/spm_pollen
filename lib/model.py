import os
import pandas as pd
import rpy2.robjects as ro

from rpy2.robjects import pandas2ri
from typing import List
from pathlib import Path
from lib.python.func import r_checkpackage


# path
path = Path(os.getcwd())

# check whether r packages exist and download if not
r_checkpackage("Epi")


class ModelGLM():
    def __init__(
        self,
        city: str,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        lag_or_ma: bool,
        # num_lags: int,
        outcome: str,
        exposure: str,
        interactive: str,
        confounding: List[str],
        temp_bool: bool,
        temp_moving_average: int,
        current_lag: int
    ):
        self.city = city
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.lag_or_ma = lag_or_ma
        # self.num_lags = num_lags
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.temp_bool = temp_bool
        self.temp_moving_average = temp_moving_average
        self.current_lag = current_lag

    def calculate_iqr(self, data) -> float:
        """[Calculates and returns inter-quartile range.]

        Args:
            data ([pd.DataFrame]): [Dataframe.]

        Returns:
            [float]: [Inter-quartile range.]
        """
        q1 = data[self.exposure].quantile(.25)
        q3 = data[self.exposure].quantile(.75)

        return q3 - q1

    def eq_creator(self):
        for i, i_element in enumerate(self.confounding):
            if i_element == "Tave":
                i_element = f"ns({i_element}, df=5)"

            if i_element == f"Tave_ma{self.current_lag}":
                i_element = f"ns({i_element}, df=5)"

            if i_element == "doy":
                i_element = f"ns({i_element}, df=5):factor(year)"

            if (i_element == "dow") | (i_element == "holiday"):
                i_element = f"factor({i_element})"

            if i == 0:
                x = i_element

            else:
                x = x + " + " + i_element

        # non-interactive
        eq1 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag} + " +
            f"{self.exposure}_{self.current_lag} + {x}"
        )

        # interactive
        eq2 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag}" +
            f":factor({self.interactive}_{self.current_lag}) + " +
            f"{self.exposure}_{self.current_lag} + {x}"
        )

        return eq1, eq2

    def export_results(self, path: Path, results: pd.DataFrame):
        if os.path.exists(path):
            old_results = pd.read_csv(path)
            old_results = pd.concat([old_results, results], ignore_index=True)
            old_results.to_csv(path, index=False)
        else:
            results.to_csv(path, index=False)

    def r_glm(self, data):
        eq1, eq2 = self.eq_creator()

        iqr = self.calculate_iqr(data)
        data[self.exposure] = data[self.exposure]/iqr

        pandas2ri.activate()
        ro.globalenv["data"] = ro.conversion.py2rpy(data)
        ro.globalenv["equation1"] = eq1
        ro.globalenv["equation2"] = eq2
        ro.globalenv["city"] = self.city
        ro.globalenv["iqr"] = iqr
        ro.globalenv["start_year"] = self.start_year
        ro.globalenv["end_year"] = self.end_year
        ro.globalenv["start_month"] = self.start_month
        ro.globalenv["end_month"] = self.end_month
        ro.globalenv["exposure"] = self.exposure
        ro.globalenv["interactive"] = self.interactive
        ro.globalenv["outcome"] = self.outcome
        ro.globalenv["current_lag"] = self.current_lag
        ro.globalenv["lag_or_ma"] = self.lag_or_ma
        ro.r.source("lib/r/glm.r")
        results = ro.globalenv["results"]
        results = ro.conversion.rpy2py(results)

        self.export_results(path=path / "results/results.csv", results=results)
