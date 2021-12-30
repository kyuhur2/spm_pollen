import os
import numpy as np
import pandas as pd
import rpy2.robjects as ro

from rpy2.robjects import pandas2ri
from typing import List
from pathlib import Path


# path
path = Path(os.getcwd())


class ModelGLM:
    def __init__(
        self,
        city: str,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        lag_or_ma: bool,
        outcome: str,
        exposure: str,
        interactive: str,
        confounding: List[str],
        current_lag: int
    ):
        self.city = city
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.lag_or_ma = lag_or_ma
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.current_lag = current_lag

    def calculate_iqr(self, data):
        """
        Calculates and returns inter-quartile range.

        Args:
            data (pd.DataFrame): Dataframe.

        Returns:
            q3 - q1 (float): Inter-quartile range.
        """
        q1 = data[self.exposure].quantile(.25)
        q3 = data[self.exposure].quantile(.75)

        return q3 - q1

    def eq_creator(self):
        """
        Creates equations for model 1 and model 2.

        Returns:
            eq1, eq2 (str, str): Equation 1 and equation 2.
        """
        for i, i_ele in enumerate(self.confounding):
            if i_ele == "Tave":
                i_ele = f"ns({i_ele}, df=5)"

            if i_ele == "Tave_ma20":
                i_ele = f"ns({i_ele}, df=5)"

            if i_ele == "doy":
                i_ele = f"ns({i_ele}, df=5):factor(year)"

            if (i_ele == "dow") | (i_ele == "holiday") | (i_ele == "ad"):
                i_ele = f"factor({i_ele})"

            if i == 0:
                x = i_ele

            else:
                x = x + " + " + i_ele

        # non-interactive
        eq1 = f"{self.outcome} ~ {self.exposure}_{self.current_lag} + {x}"

        # interactive
        eq2 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag}" +
            f":factor({self.interactive}_{self.current_lag}) + " +
            f"{self.exposure}_{self.current_lag} + {x}"
        )

        return eq1, eq2

    def export_data(self, path: Path, data: pd.DataFrame):
        """
        Exports data to path.

        Args:
            path (Path): Path to export to.
            data (pd.DataFrame): Data.
        """
        if os.path.exists(path):
            old_data = pd.read_csv(path)
            old_data = pd.concat([old_data, data], ignore_index=True)
            old_data.to_csv(path, index=False)
        else:
            data.to_csv(path, index=False)

    def interactive_glm(self, data, eq1, eq2):
        pandas2ri.activate()
        ro.globalenv["data"] = ro.conversion.py2ri(data)
        ro.globalenv["equation1"] = eq1
        ro.globalenv["equation2"] = eq2
        ro.globalenv["exposure"] = self.exposure
        ro.globalenv["outcome"] = self.outcome
        ro.globalenv["interactive"] = self.interactive
        ro.r.source("lib/r/r_interactive_glm.r")

        exp1 = ro.conversion.ri2py(ro.globalenv["exp1"])
        exp2 = ro.conversion.ri2py(ro.globalenv["exp2"])
        sum1 = ro.conversion.ri2py(ro.globalenv["sum1"])
        sum2 = ro.conversion.ri2py(ro.globalenv["sum2"])

        exp1 = exp1.set_index("None")
        exp2 = exp2.set_index("None")
        sum1 = sum1.set_index("None")
        sum2 = sum2.set_index("None")

        return exp1, exp2, sum1, sum2

    def model(self, data):
        eq1, eq2 = self.eq_creator()
        iqr = self.calculate_iqr(data)
        data[self.exposure] = data[self.exposure]/iqr

        # results from glm
        exp1, exp2, sum1, sum2 = self.interactive_glm(data, eq1, eq2)

        # dataframe specifications
        exposure_lag = self.exposure + "_" + str(self.current_lag)
        exposure_lag_interactive = (
            exposure_lag + ":factor(" + self.interactive + "_" +
            str(self.current_lag) + ")"
        )

        if self.lag_or_ma is True:
            lag_or_ma = "lag"
        else:
            lag_or_ma = "ma"

        num_rows = 5
        col_names = [
            "city",
            "start_year",
            "end_year",
            "start_month",
            "end_month",
            "exposure",
            "interactive",
            "outcome",
            "lag_or_ma",
            "lag",
            "iqr",
            "quantile",
            "equation",
            "rr",
            "cil",
            "ciu",
            "B",
            "se"
        ]

        # create results df
        results = []
        results.append(pd.DataFrame(np.repeat(self.city, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.start_year, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.end_year, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.start_month, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.end_month, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.exposure, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.interactive, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.outcome, num_rows)))
        results.append(pd.DataFrame(np.repeat(lag_or_ma, num_rows)))
        results.append(pd.DataFrame(np.repeat(self.current_lag, num_rows)))
        results.append(pd.DataFrame(np.repeat(iqr, num_rows)))
        results.append(pd.DataFrame(range(0, 5)))
        results.append(pd.Series([eq2] * num_rows))

        # relative risk, confidence interval lower/upper
        rr_cil_ciu = pd.concat([
            exp1.loc[[exposure_lag], :],
            exp2[exp2.index.str.startswith(self.exposure)]
        ], ignore_index=True)
        results.append(rr_cil_ciu)

        # B, se
        results.append(
            pd.DataFrame(
                [
                    sum1.loc[exposure_lag, :]["Estimate"],
                    sum2.loc[exposure_lag, :]["Estimate"],
                    sum2.loc[exposure_lag_interactive + "1", :]["Estimate"],
                    sum2.loc[exposure_lag_interactive + "2", :]["Estimate"],
                    sum2.loc[exposure_lag_interactive + "3", :]["Estimate"]
                ]
            )
        )
        results.append(
            pd.DataFrame(
                [
                    sum1.loc[exposure_lag, :]["Std. Error"],
                    sum2.loc[exposure_lag, :]["Std. Error"],
                    sum2.loc[exposure_lag_interactive + "1", :]["Std. Error"],
                    sum2.loc[exposure_lag_interactive + "2", :]["Std. Error"],
                    sum2.loc[exposure_lag_interactive + "3", :]["Std. Error"]
                ]
            )
        )

        # concatenate & rename columns
        results = pd.concat(results, ignore_index=True, axis=1)
        results.columns = col_names

        # save results
        self.export_data(
            path / "results/results.csv",
            data=results
        )
