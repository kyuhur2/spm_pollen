import os
import pandas as pd
import rpy2.robjects as robjects

from typing import List
from pathlib import Path
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr


# path
path = Path(os.getcwd())

# download r packages
utils = importr('utils')
utils.install_packages("Epi", repos="https://cloud.r-project.org")


class ModelGLM():
    def __init__(
        self,
        city: str,
        # num_lags: int,
        # moving_average: int,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        outcome: str,
        exposure: str,
        interactive: str,
        confounding: List[str],
        temp_bool: bool,
        temp_moving_average: int,
        current_lag_ma: int
    ):
        self.city = city
        # self.num_lags = num_lags
        # self.moving_average = moving_average
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.temp_bool = temp_bool
        self.temp_moving_average = temp_moving_average
        self.current_lag_ma = current_lag_ma

    def eq_creator(self):
        for i, i_element in enumerate(self.confounding):
            if i_element == "Tave":
                i_element = f"ns({i_element}, df=5)"

            if i_element == f"Tave_ma{self.current_lag_ma}":
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
            f"{self.outcome} ~ {self.exposure}_{self.current_lag_ma} + " +
            f"{self.exposure}_{self.current_lag_ma} + {x}"
        )

        # interactive
        eq2 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag_ma}" +
            f":factor({self.interactive}_{self.current_lag_ma}) + " +
            f"{self.exposure}_{self.current_lag_ma} + {x}"
        )

        return eq1, eq2

    def export_results(self, path: Path, results: pd.DataFrame):
        path_name = path / "results/results.csv"

        if os.path.exists(path_name):
            old_results = pd.read_csv(path_name)
            old_results = pd.concat([old_results, results], ignore_index=True)
            old_results.to_csv(path_name, index=False)
        else:
            results.to_csv(path_name, index=False)

    def r_glm(self, data):
        eq1, eq2 = self.eq_creator()

        pandas2ri.activate()
        robjects.globalenv["data"] = pandas2ri.py2ri(data)
        robjects.globalenv["equation1"] = eq1
        robjects.globalenv["equation2"] = eq2
        robjects.globalenv["city"] = self.city
        robjects.globalenv["start_year"] = self.start_year
        robjects.globalenv["end_year"] = self.end_year
        robjects.globalenv["start_month"] = self.start_month
        robjects.globalenv["end_month"] = self.end_month
        robjects.globalenv["exposure"] = self.exposure
        robjects.globalenv["interactive"] = self.interactive
        robjects.globalenv["outcome"] = self.outcome
        robjects.globalenv["current_lag"] = self.current_lag_ma
        robjects.r.source("lib/glm.r")
        results = robjects.globalenv["results"]
        results = pandas2ri.ri2py_dataframe(results)

        self.export_results(path=path, results=results)
