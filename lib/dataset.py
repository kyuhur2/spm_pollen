import os
import pandas as pd

from typing import List
from pathlib import Path


path = Path(os.getcwd())
data = pd.read_csv(path / "data/cleaned_data.csv")


class ImportAndCleanData:
    def __init__(
        self,
        city: str,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        lag_or_ma: bool,
        num_lags: int,
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
        self.num_lags = num_lags
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.temp_bool = temp_bool
        self.temp_moving_average = temp_moving_average
        self.current_lag = current_lag

    def create_lags(self, data: pd.DataFrame):
        """[Creates lags and moving averaged columns.]

        Args:
            data ([pd.DataFrame]): [A dataframe with exposure column.]

        Returns:
            [pd.DataFrame]: [A dataframe with lagged and moving averaged
            columns appended.]
        """
        # lags for exposure, interactive
        if self.lag_or_ma is True:
            data[self.exposure + "_" + str(self.current_lag)] = data[
                self.exposure].shift(self.current_lag)
            data[self.interactive + "_" + str(self.current_lag)] = data[
                self.interactive].shift(self.current_lag)
        else:
            data[self.exposure + "_ma" + str(self.current_lag)] = data[
                self.exposure].rolling(window=self.current_lag).mean()
            data[self.interactive + "_ma" + str(self.current_lag)] = data[
                self.interactive].rolling(window=self.current_lag).mean()

        # ma for temperature
        data[f"Tave_ma{self.temp_moving_average}"] = data["Tave"].rolling(
            window=self.temp_moving_average).mean()

        return data

    def categorize_interactive(self, data):
        if self.lag_or_ma is True:
            interactive_lag = self.interactive + "_" + str(self.current_lag)
        else:
            interactive_lag = self.interactive + "_ma" + str(self.current_lag)

        # turn into quantiles
        data[interactive_lag] = pd.qcut(
            data[interactive_lag], 4, labels=False)

        # print number of NA counts
        print("Number of NA counts:" + str(data[interactive_lag].isna().sum()))

        # get rid of NA
        data.dropna(subset=[interactive_lag], inplace=True)

        return data

    def clean_data(self):
        # drop rows based on PREFECTURE - necessary to create lag & ma cols
        cleaned_data = data[(data.city == self.city)]

        # create lags & ma
        cleaned_data = self.create_lags(cleaned_data)

        # drop rows
        cleaned_data = cleaned_data[
            (cleaned_data["year"] >= self.start_year) &
            (cleaned_data["year"] <= self.end_year) &
            (cleaned_data["month"] >= self.start_month) &
            (cleaned_data["month"] <= self.end_month)
        ]

        # cols to keep
        if self.lag_or_ma is True:
            a = [f"{self.exposure}_{self.current_lag}"]
            b = [f"{self.interactive}_{self.current_lag}"]
        else:
            a = [f"{self.exposure}_ma{self.current_lag}"]
            b = [f"{self.interactive}_ma{self.current_lag}"]

        col_names = [
            "date", "city", "year", "month", self.outcome, self.exposure,
            self.interactive
        ] + a + b + self.confounding

        # drop cols based on col_names
        cleaned_data = cleaned_data[col_names]

        # categorize interactive column
        cleaned_data = self.categorize_interactive(cleaned_data)

        return cleaned_data
