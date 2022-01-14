# SPM Pollen Project

Contains code for a project in the works, investigating how pollen modifies the association between air pollution and mortality.

Below is a graphical abstract that describes the project. This graphical abstract was published as part of the 2021 ISEE Conference. The conference abstract can be accessed [here](https://ehp.niehs.nih.gov/doi/abs/10.1289/isee.2021.P-594).

![Graphical Abstract](https://github.com/kyuhur2/spm_pollen/blob/main/images/graphical_abstract.png?raw=true)

# List of To-Dos

**Setup**

| Completed | Task                 |
| --------- | -------------------- |
| ✅        | Anaconda environment |
| ✅        | Black linter         |
| ✅        | Pre-commit           |
| ✅        | Requirements.txt     |

**Progress**

| Completed | Task                 |
| --------- | -------------------- |
| ✅        | Data pre-processing  |
| ❌        | Descriptive analysis |
| ✅        | Model selection      |
| ✅        | Individual analysis  |
| ❌        | Aggregated analysis  |
| ❌        | Tables               |
| ❌        | Figures              |
| ❌        | Tests                |

**Docs**

| Completed | Task       |
| --------- | ---------- |
| ❌        | Manuscript |
| ❌        | References |

# Project Layout

The project flow is described in the diagram below.

![Project Flow Diagram](https://github.com/kyuhur2/spm_pollen/blob/main/images/project_flow_diagram.png)

A tree of the project files and folders are provided below.

    spm_pollen/
    │
    ├── data/  # not committed to github, data is private
    │   ├── cleaned_data.csv
    │   └── misc/
    │       ├── air pollution station geocodes.csv
    │       └── clinic station geocodes.csv
    │
    ├── docs/  # not committed to github, docs are private currently
    │   ├── docx_reference.docx
    │   ├── docx_template.docx
    │   ├── docx_template.rmd
    │   ├── plos.csv
    │   └── r-references.bib
    │
    ├── images/
    │   └── graphical_abstract.png
    │
    ├── lib/
    │   ├── dataset.py
    │   ├── install_r_packages.py
    │   ├── model.py
    │   ├── printargs.py
    │   ├── sensitivity_analysis.py
    │   └── r/
    │       ├── r_interactive_anova.r
    │       ├── r_interactive_glm.r
    │       ├── r_interactive_qaic.r
    │       └── r_metafor.r
    │
    ├── misc/
    │   └── cmdscript_writer.py
    │
    ├── model/
    │   ├── confounding.json
    │   └── qaics.csv
    │
    ├── results/
    │   └── results.csv
    │
    ├── src/
    │   ├── aggregate_models.py
    │   ├── determine_model.py
    │   ├── model_selection.py
    │   └── run_models.py
    │
    ├── determine_model.py
    ├── model_selection.py
    ├── run_model.py
    ├── script.bat
    ├── environment.yml
    └── README.md

# General Issues

1. `conda` and `pre-commit`

There's a known conflict issue between `conda` and `pre-commit` originating from how git hooks are generated for python versions under `3.9`. `pre-commit install` python executables are stored in generated git hooks, but a `conda` environment executes the installed python version only when the environment is activated. To circumvent this issue, there are three possible ways to solve this, as documented [here](https://github.com/conda-forge/pre-commit-feedstock/issues/9):

- Activate the environment in the terminal, open vscode from the activated terminal using the command `code .` **(tested)**
- Create [exec-wrappers](https://github.com/gqmelo/exec-wrappers) and [conda-wrappers](https://github.com/conda-forge/conda-wrappers-feedstock) that mimic a conda activation before running the executable **(not tested)**
- Reinstall conda with python versions `3.9` or `3.10` **(not tested)**

# Project-specific Issues

1. `rpy2`

Environment should be set up with `requirements.txt`; `rpy2`==2.9.4 should be installed with `conda` not `pip` (latest version has issues with R/vscode). The **rpy2.robjects.pandas2ri.ri2py_dataframe** function should be altered as suggested [here](https://github.com/rpy2/rpy2/issues/680) for this project to work.

    def ri2py_dataframe(obj):
        # items = tuple((k, ri2py(v)) for k, v in obj.items())
        # res = PandasDataFrame.from_items(items)
        items = OrderedDict((k, ri2py(v)) for k, v in obj.items())
        res = PandasDataFrame.from_dict(items)
        return res
