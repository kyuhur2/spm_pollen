import os
import pandas as pd

from typing import List
from pathlib import Path


path = Path(os.getcwd())
data = pd.read_csv(path / "data/cleaned_data.csv")


class ImportAndCleanData():
    def __init__(
        self,
        city: str,
        num_lags: int,
        moving_average: int,
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
        self.num_lags = num_lags
        self.moving_average = moving_average
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

    def create_lags_ma(self, data: pd.DataFrame):
        """[Creates lags and moving averaged columns.]

        Args:
            data ([pd.DataFrame]): [A dataframe with exposure column.]

        Returns:
            [pd.DataFrame]: [A dataframe with lagged and moving averaged
            columns appended.]
        """
        # lags for exposure, interactive
        for i in range(self.num_lags):
            data[self.exposure + "_" + str(i + 1)] = data[
                self.exposure].shift(i + 1)
            data[self.interactive + "_" + str(i + 1)] = data[
                self.interactive].shift(i + 1)

        # ma for exposure, interactive
        for i in range(self.moving_average):
            data[self.exposure + "_ma" + str(i + 1)] = data[
                self.exposure].rolling(window=i + 1).mean()
            data[self.interactive + "_ma" + str(i + 1)] = data[
                self.interactive].rolling(window=i + 1).mean()

        # ma for temperature
        data[f"Tave_ma{self.temp_moving_average}"] = data["Tave"].rolling(
            window=self.temp_moving_average).mean()

        return data

    def categorize_interactive(self, data):
        interactive_lag = self.interactive + "_" + str(self.current_lag_ma)

        # turn into quantiles
        data[interactive_lag] = pd.qcut(
            data[interactive_lag], 4, labels=False)

        # print number of NA counts
        print(data[interactive_lag].isna().sum())

        # get rid of NA
        data.dropna(subset=[interactive_lag], inplace=True)

        return data

    def clean_data(self):
        # drop rows based on PREFECTURE - necessary to create lag & ma cols
        cleaned_data = data[(data.city == self.city)]

        # create lags & ma
        cleaned_data = self.create_lags_ma(cleaned_data)

        # drop rows
        cleaned_data = cleaned_data[
            (cleaned_data["year"] >= self.start_year) &
            (cleaned_data["year"] <= self.end_year) &
            (cleaned_data["month"] >= self.start_month) &
            (cleaned_data["month"] <= self.end_month)
        ]

        # cols to keep
        a = [f"{self.exposure}_{i + 1}" for i in range(self.num_lags)]
        b = [f"{self.exposure}_ma{i + 1}" for i in range(self.moving_average)]
        c = [f"{self.interactive}_{i + 1}" for i in range(self.num_lags)]
        d = [f"{self.interactive}_ma{i + 1}" for i in range(
            self.moving_average)]
        col_names = [
            "date", "city", "year", "month", self.outcome, self.exposure,
            self.interactive
        ] + a + b + c + d + self.confounding

        # drop cols based on col_names
        cleaned_data = cleaned_data[col_names]

        # categorize interactive column
        cleaned_data = self.categorize_interactive(cleaned_data)

        return cleaned_data
