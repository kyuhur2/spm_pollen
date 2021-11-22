import argparse
import pandas as pd

from lib.model import ModelGLM
from lib.dataset import ImportAndCleanData
from lib.printargs import printargs, println  # noqa


pd.options.mode.chained_assignment = None

args_list = [
    # data configurations
    "city",                 # 1
    "start_year",           # 2
    "end_year",             # 3
    "start_month",          # 4
    "end_month",            # 5
    "num_lags",             # 6
    "moving_average",       # 7

    # model configurations
    "outcome",              # 8
    "exposure",             # 9
    "interactive",          # 10
    "confounding",          # 11
    "temp_bool",            # 12
    "temp_moving_average",  # 13
    "current_lag_ma"        # 14
]

parser = argparse.ArgumentParser()
parser.add_argument(f"--{args_list[0]}", type=str, default="Fukuoka")
parser.add_argument(f"--{args_list[1]}", type=int, default=1989)
parser.add_argument(f"--{args_list[2]}", type=int, default=2014)
parser.add_argument(f"--{args_list[3]}", type=int, default=2)
parser.add_argument(f"--{args_list[4]}", type=int, default=4)
parser.add_argument(f"--{args_list[5]}", type=int, default=7)
parser.add_argument(f"--{args_list[6]}", type=int, default=7)
parser.add_argument(f"--{args_list[7]}", type=str, default="All")
parser.add_argument(f"--{args_list[8]}", type=str, default="SPMout")
parser.add_argument(f"--{args_list[9]}", type=str, default="suhiout")
parser.add_argument(f"--{args_list[10]}", type=str, default=[
    "Tave", "RHave", "dow", "doy", "holiday"])
parser.add_argument(f"--{args_list[11]}", type=bool, default=True)
parser.add_argument(f"--{args_list[12]}", type=int, default=20)
parser.add_argument(f"--{args_list[13]}", type=int, default=1)

args = parser.parse_args()
city = args.city
start_year = args.start_year
end_year = args.end_year
start_month = args.start_month
end_month = args.end_month
num_lags = args.num_lags
moving_average = args.moving_average
outcome = args.outcome
exposure = args.exposure
interactive = args.interactive
confounding = args.confounding
temp_bool = args.temp_bool
temp_moving_average = args.temp_moving_average
current_lag_ma = args.current_lag_ma

# add Tave_ma20 as a confounding variable
confounding.append("Tave_ma" + str(temp_moving_average))

printargs(
    args_list,
    args_val=[
        city,
        start_year,
        end_year,
        start_month,
        end_month,
        num_lags,
        moving_average,

        outcome,
        exposure,
        interactive,
        confounding,
        temp_bool,
        temp_moving_average,
        current_lag_ma
    ]
)

# data
init_dataset = ImportAndCleanData(
    city=city,
    start_year=start_year,
    end_year=end_year,
    start_month=start_month,
    end_month=end_month,
    num_lags=num_lags,
    moving_average=moving_average,
    outcome=outcome,
    exposure=exposure,
    interactive=interactive,
    confounding=confounding,
    temp_bool=temp_bool,
    temp_moving_average=temp_moving_average,
    current_lag_ma=current_lag_ma
)

data = init_dataset.clean_data()

# model
init_model = ModelGLM(
    city=city,
    # num_lags=num_lags,
    # moving_average=moving_average,
    start_year=start_year,
    end_year=end_year,
    start_month=start_month,
    end_month=end_month,
    outcome=outcome,
    exposure=exposure,
    interactive=interactive,
    confounding=confounding,
    temp_bool=temp_bool,
    temp_moving_average=temp_moving_average,
    current_lag_ma=current_lag_ma
)

model = init_model.r_glm(data=data)