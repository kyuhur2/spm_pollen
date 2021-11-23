# SPM Pollen Project
  
Something

*Note  
  
Change the **rpy2.robjects.pandas2ri.ri2py_dataframe** function as suggested here: https://github.com/rpy2/rpy2/issues/680  
  
    def ri2py_dataframe(obj):  
        # items = tuple((k, ri2py(v)) for k, v in obj.items())  
        # res = PandasDataFrame.from_items(items)  
        items = OrderedDict((k, ri2py(v)) for k, v in obj.items())  
        res = PandasDataFrame.from_dict(items)  
        return res  
  
