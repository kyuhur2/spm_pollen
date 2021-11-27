import os

from pathlib import Path


"""
Creates a .bat file which contains a command line script that iterates for
every variable.

In the current project, the variables are:
 - city
 - lag
"""

path = Path(os.getcwd())

cities = [
    "Fukuoka",
    "Kumamoto",
    "Nagasaki",
    "Oita",
    "Saga",
    "Kagoshima",
    "Miyazaki",
    "Kitakyushu"
]

lags = [i for i in range(1, 6)]

lag_or_ma = [True, False]

script = ["@echo off", "\n", ]
for i in lag_or_ma:
    for j in cities:
        for k in lags:
            line = (
                f"python main.py --lag_or_ma {i} --city {j} --num_lags {k}\n"
            )
            script.append(line)

script.append("@pause")

with open(os.path.join(path.parent / "script.bat"), "w") as OPATH:
    OPATH.writelines(script)
