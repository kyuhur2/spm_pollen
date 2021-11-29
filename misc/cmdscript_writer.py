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

lags = [i for i in range(1, 6)]
lag_or_ma = [True, False]
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

# activate conda
script = [
    "@echo off\n",
    f"cd {path.parent}\n",
    "del /f model\\qaics.csv\n",
    "del /f results\\results.csv\n",
    "call conda activate spm_pollen\n",
]

# model selection
for i in lag_or_ma:
    for j in cities:
        for k in lags:
            line = (
                "python model_selection.py " +
                f"--lag_or_ma {i} --city {j} --num_lags {k}\n"
            )
            script.append(line)

# determine confounding variables based on AIC
script.append("python determine_model.py\n")

# run model
for i in lag_or_ma:
    for j in cities:
        for k in lags:
            line = (
                "python run_model.py " +
                f"--lag_or_ma {i} --city {j} --num_lags {k}\n"
            )
            script.append(line)

# deactivate conda
script.append("call conda deactivate\n")
script.append("@pause")

with open(os.path.join(path.parent / "script.bat"), "w") as OPATH:
    OPATH.writelines(script)
