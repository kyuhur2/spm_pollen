import os
import numpy as np
import pandas as pd
import rpy2.robjects as ro

from typing import List
from pathlib import Path
from rpy2.robjects import pandas2ri
from itertools import chain, combinations


# path
path = Path(os.getcwd())


class ModelQAIC:
    def __init__(
        self,
        outcome: str,
        exposure: str,
        interactive: str,
        confounding: List[str],
        current_lag: int
    ):
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.current_lag = current_lag

    def calculate_iqr(self, data) -> float:
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

    def eq_creator(self, confounding):
        """
        Creates equations for model 1 (non-interactive) and model 2
        (interactive).

        Returns:
            eq1, eq2 (str, str): Equation 1 and equation 2.
        """
        for i, i_ele in enumerate(confounding):
            if i_ele == "Tave":
                i_ele = f"ns({i_ele}, df=5)"

            if i_ele == f"Tave_ma{self.current_lag}":
                i_ele = f"ns({i_ele}, df=5)"

            if i_ele == "doy":
                i_ele = f"ns({i_ele}, df=5):factor(year)"

            if (i_ele == "dow") | (i_ele == "holiday") | (i_ele == "ad"):
                i_ele = f"factor({i_ele})"

            if i == 0:
                x = i_ele

            else:
                x = x + " + " + i_ele

        if (confounding == []) | (confounding is None):
            eq1 = f"{self.outcome} ~ {self.exposure}_{self.current_lag}"
            eq2 = (
                f"{self.outcome} ~ {self.exposure}_{self.current_lag}" +
                f":factor({self.interactive}_{self.current_lag}) + " +
                f"{self.exposure}_{self.current_lag}"
            )
        else:
            eq1 = f"{self.outcome} ~ {self.exposure}_{self.current_lag} + {x}"
            eq2 = (
                f"{self.outcome} ~ {self.exposure}_{self.current_lag}" +
                f":factor({self.interactive}_{self.current_lag}) + " +
                f"{self.exposure}_{self.current_lag} + {x}"
            )

        return eq1, eq2

    def powerset_generator(self, confounding):
        for i in chain.from_iterable(combinations(
                confounding, j) for j in range(len(confounding) + 1)):
            yield list(i)

    def export_data(self, path: Path, data: pd.DataFrame):
        """
        Exports data path.

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

    def interactive_qaic(self, data, eq1, eq2):
        pandas2ri.activate()
        ro.globalenv["data"] = ro.conversion.py2ri(data)
        ro.globalenv["equation1"] = eq1
        ro.globalenv["equation2"] = eq2
        ro.globalenv["exposure"] = self.exposure
        ro.globalenv["outcome"] = self.outcome
        ro.globalenv["interactive"] = self.interactive
        ro.r.source("lib/r/r_interactive_qaic.r")

        model1 = ro.conversion.ri2py(ro.globalenv["model1"])
        model2 = ro.conversion.ri2py(ro.globalenv["model2"])
        qaic1 = ro.globalenv["qaic1"]
        qaic2 = ro.globalenv["qaic2"]

        return model1, model2, qaic1, qaic2

    def best_model(self, data):
        confs, eq1s, eq2s = [], [], []
        model1s, model2s, qaic1s, qaic2s = [], [], [], []
        for conf in self.powerset_generator(self.confounding):
            eq1, eq2 = self.eq_creator(conf)
            iqr = self.calculate_iqr(data)
            data[self.exposure] = data[self.exposure]/iqr

            # calculate aic
            model1, model2, qaic1, qaic2 = self.interactive_qaic(
                data, eq1, eq2)

            # save identifying values
            confs.append(conf)
            eq1s.append(eq1)
            eq2s.append(eq2)
            model1s.append(model1)
            model2s.append(model2)
            qaic1s.append(np.floor(qaic1[0]))
            qaic2s.append(np.floor(qaic2[0]))

        # create qaic dataframe and export
        qaics = pd.DataFrame(
            {
                'Outcome Variable': np.repeat(self.outcome, len(eq1s)),
                'Exposure Variable': np.repeat(self.exposure, len(eq1s)),
                'Interactive Variable': np.repeat(self.interactive, len(eq1s)),
                'Current Lag': np.repeat(self.current_lag, len(eq1s)),
                'Confounding Variables': confs,
                'Equation 1': eq1s,
                'Equation 2': eq2s,
                'QAIC of Equation 1': qaic1s,
                'QAIC of Equation 2': qaic2s
            }
        )

        self.export_data(
            path=path / "model/qaics.csv",
            data=qaics
        )

    def best_confounding_qaic(self):
        qaics = pd.read_csv(path / "model/qaics.csv")
        conf = qaics.loc[qaics["QAIC of Equation 2"].idxmin()]
        conf = conf["Confounding Variables"].split("','")

        return conf
