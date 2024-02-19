import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":

    data = pd.read_csv("data/merged.csv", index_col=0)
    
    description = data.describe()
    
    description.to_csv("data/output/description.csv")

    data_for_corr = data.drop([
        "Entry ID", "Actor type", "Subject ID", "Hospital ID", "Group ID",
        "anonymised ID"
    ], axis=1)
    print(data_for_corr.columns)

    corr_mat = data_for_corr.corr()
    corr_mat.to_csv("data/output/corr_mat.csv")

    facets_cols = [x for x in data.columns if "_" in x]
    print(facets_cols)
    cats = []
    for col in data.columns:
        if "_" in col:
            cat = col.split("_")[0]
            print(cat)
            cats.append(cat)
    cats = set(cats)
    print(cats)

    for facets_item in facets_cols:
        rest_of_cols = [x for x in data_for_corr.columns if x not in facets_item]
        for sdq_item in rest_of_cols:
            plot = data_for_corr[[facets_item, sdq_item]].plot(kind="scatter", x=facets_item, y=sdq_item)
            plt.savefig(f"data/plots/per_column/{facets_item}_{sdq_item}_scatter_matrix.png")