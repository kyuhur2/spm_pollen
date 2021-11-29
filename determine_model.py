import os
import json
import pandas as pd

from pathlib import Path


# import data
path = Path(os.getcwd())
qaics = pd.read_csv(path / "model/qaics.csv")

# group by confounding variables
qaics_group = qaics.groupby(["Confounding Variables"]).mean()
qaics_group.reset_index(inplace=True)
del qaics_group["Current Lag"]

# determine best confounding combination by eq1, eq2
eq1min = qaics_group.loc[qaics_group["QAIC of Equation 1"].idxmin()]
eq2min = qaics_group.loc[qaics_group["QAIC of Equation 2"].idxmin()]

if eq1min["Confounding Variables"] == eq2min["Confounding Variables"]:
    print("Best model is the same for eq1 and eq2.")
else:
    print("Best model is different. Defaulting to eq2.")

# get rid of brackets, quotations and put into a list
x = eq2min["Confounding Variables"]
if (x.count(',') + 1) >= 2:
    conf = x.replace("[", "").replace("]", "").replace("'", "").split(", ")
elif x != "":
    conf = [x.replace("[", "").replace("]", "").replace("'", "")]
else:
    conf = []

# save conf as a variable
with open(path / "model/confounding.json", "w") as f:
    json.dump(conf, f)
