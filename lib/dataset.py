import os
import pandas as pd

from pathlib import Path


path = Path(os.getcwd())
data = pd.read_csv(path / "data/cleaned_data.csv")


class ImportAndCleanData():
    def __init__(
        self,
        city: str,
        lags: int,
        moving_average: int,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        outcome: str,
        exposure: str,
        interactive: str
    ):
        self.city = city
        self.lags = lags
        self.moving_average = moving_average
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive

    def create_lags_ma(self, data):
        for i in range(self.lags):
            data[self.exposure + "_" + str(i + 1)] = data[
                self.exposure].shift(i + 1)
            data[self.interactive + "_" + str(i + 1)] = data[
                self.interactive].shift(i + 1)

        for i in range(self.moving_average):
            data[self.exposure + "_ma" + str(i + 1)] = data[
                self.exposure].rolling(window=i + 1).mean()
            data[self.interactive + "_ma" + str(i + 1)] = data[
                self.interactive].rolling(window=i + 1).mean()

        return data

    def clean_data(self):
        # drop rows based on PREFECTURE - necessary to create lag & ma cols
        cleaned_data = data[(data.city == self.city)]

        # create lags & ma
        cleaned_data = self.create_lags_ma(cleaned_data)

        # drop rows
        cleaned_data = cleaned_data[
            ((cleaned_data.year >= self.start_year) &
                (cleaned_data.year <= self.end_year)) &
            ((cleaned_data.month >= self.start_month) &
                (cleaned_data.month <= self.end_month))
        ]

        # drop cols
        a = [f"{self.exposure}_{i + 1}" for i in range(self.lags)]
        b = [f"{self.exposure}_ma{i + 1}" for i in range(self.moving_average)]
        c = [f"{self.interactive}_{i + 1}" for i in range(self.lags)]
        d = [f"{self.interactive}_ma{i + 1}" for i in range(
            self.moving_average)]
        col_names = [
            "date", "city", "year", "month", self.outcome, self.exposure,
            self.interactive] + a + b + c + d
        cleaned_data = cleaned_data[col_names]

        return cleaned_data

    def main(self):
        cleaned_data = self.clean_data()
        return cleaned_data
