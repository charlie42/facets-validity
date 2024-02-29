import pandas as pd
import numpy as np
import statsmodels.api as sm

def run_ols(data, facets_cols, sdq_subscales):
    results = {}
    for subscale in sdq_subscales:
        mod = sm.OLS(data[subscale], data[facets_cols])
        result = mod.fit()
        results[subscale] = result
        print(subscale, result.summary())
    return results

def write_results_to_csv(results):
    import os   
    dir = "output/paper/ols/"
    if not os.path.exists(dir):
        os.makedirs(dir)

    for subscale in results:

        file_name = f"{dir}{subscale}_full.csv" 
        with open(file_name, 'w') as f:
            f.write(results[subscale].summary().as_csv())

            # Read and reformat as df
            df = pd.read_csv(file_name)
            print(df)


if __name__ == "__main__":    

    data = pd.read_csv("data/merged_split_by_anchor.csv")
    
    facets_cols = [col for col in data.columns if "_" in col]
    sdq_subscales = ["emotion", "conduct", "hyper", "peer",	"prosoc", "tot"]

    ols_results = run_ols(data, facets_cols, sdq_subscales)
    write_results_to_csv(ols_results)

        

    