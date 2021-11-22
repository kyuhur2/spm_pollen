import argparse

from lib.printargs import printargs, println  # noqa
from lib.dataset import ImportAndCleanData


args_list = [
    "city", "lags", "moving_average", "start_year", "end_year", "start_month",
    "end_month", "outcome", "exposure", "interactive"
]

parser = argparse.ArgumentParser()
parser.add_argument(f"--{args_list[0]}", type=str, default="Fukuoka")
parser.add_argument(f"--{args_list[1]}", type=int, default=7)
parser.add_argument(f"--{args_list[2]}", type=int, default=7)
parser.add_argument(f"--{args_list[3]}", type=int, default=1989)
parser.add_argument(f"--{args_list[4]}", type=int, default=2014)
parser.add_argument(f"--{args_list[5]}", type=int, default=2)
parser.add_argument(f"--{args_list[6]}", type=int, default=4)
parser.add_argument(f"--{args_list[7]}", type=str, default="All")
parser.add_argument(f"--{args_list[8]}", type=str, default="SPMout")
parser.add_argument(f"--{args_list[9]}", type=str, default="suhiout")

args = parser.parse_args()
city = args.city
lags = args.lags
moving_average = args.moving_average
start_year = args.start_year
end_year = args.end_year
start_month = args.start_month
end_month = args.end_month
outcome = args.outcome
exposure = args.exposure
interactive = args.interactive

printargs(
    args_list,
    args_val=[
        city, lags, moving_average, start_year, end_year, start_month,
        end_month, outcome, exposure, interactive]
)

init_dataset = ImportAndCleanData(
    city=city,
    lags=lags,
    moving_average=moving_average,
    start_year=start_year,
    end_year=end_year,
    start_month=start_month,
    end_month=end_month,
    outcome=outcome,
    exposure=exposure,
    interactive=interactive)
data = init_dataset.main()
print(data.columns)
