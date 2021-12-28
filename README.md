# SPM Pollen Project
  
Contains code for a project in the works, investigating how pollen modifies the association between air pollution and mortality.

# Project Layout
  
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
    ├── determine_model.py  
    ├── model_selection.py  
    ├── run_model.py  
    ├── script.bat    
    ├── environment.yml  
    └── README.md  
  
# Notes  
  
Environment should be set up with `environment.yaml`; rpy2 is installed with `conda` not `pip` (latest version has issues with R/vscode)

However, should change the **rpy2.robjects.pandas2ri.ri2py_dataframe** function as suggested here: https://github.com/rpy2/rpy2/issues/680  
  
    def ri2py_dataframe(obj):  
        # items = tuple((k, ri2py(v)) for k, v in obj.items())  
        # res = PandasDataFrame.from_items(items)  
        items = OrderedDict((k, ri2py(v)) for k, v in obj.items())  
        res = PandasDataFrame.from_dict(items)  
        return res  
  
