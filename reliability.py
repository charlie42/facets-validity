import pandas as pd

df = pd.read_csv("data/facets_transformed.csv", index_col=0)
print(df.columns)
print(df[["Subject ID", "Time", "Subject-Respondent Pair ID"]])

# https://www.statology.org/intraclass-correlation-coefficient-python/