import pandas as pd 
import numpy as np
import json

def preprocess_facets(facets_data):
    from facets_preprocessing import FACETSFormatter
    formatter = FACETSFormatter(facets_data)
    df = formatter.transform()
    print(df)

    # Filter by subject group ed5e3cf6-67f0-405c-be85-f33d3184ec3a
    df = df[df["Group ID"] == "ed5e3cf6-67f0-405c-be85-f33d3184ec3a"]

    return df

def preprocess_sdq(sdq_data):

    # Remove empty rows and columns
    sdq_data = sdq_data.dropna(axis=1, how="all")
    sdq_data = sdq_data.dropna(axis=0, how="all")
    # Replace #VALUE! and -1 with np.nan
    sdq_data.replace("#VALUE!", np.nan, inplace=True)
    sdq_data.replace("-1", np.nan, inplace=True)
    # Drop where SDQ completion != 1
    sdq_data = sdq_data[sdq_data["SDQ completion"] == 1]

    # Make all columns numeric except ID
    for col in sdq_data.columns:
        if col != "anonymised ID":
            sdq_data[col] = pd.to_numeric(sdq_data[col])

    # Score
    from sdq_scoring import SDQScorer
    sdq_scorer = SDQScorer(sdq_data)
    scored_sdq = sdq_scorer.score()
    print(scored_sdq)

    return scored_sdq

def preprocess_diagnostics(data):
    # Drop rows with empty Study ID 
    data = data[~(data["Study ID"].isna())]

    # Drop where Diag completion is not 1
    data = data[data["Diag completion"] == 1]
    data = data.drop("Diag completion", axis=1)

    # Strip whitespaces
    data = data.apply(lambda col: col.str.strip())

    # Replace NaN with 0
    data = data.fillna(0)

    # Replace Y with 1, N with 0, N/A with nan
    data = data.replace({"Y": 1, "N": 0, "N/A": np.nan})

    # Add prefix to diag columns, ignore Study ID column
    data.columns = ["Diag."+x if x != "Study ID" else x for x in data.columns]

    print(data.columns)
    print(data.dtypes)

    return data

def split_by_anchor(data):
    facets_cols = [x for x in data.columns if "_" in x] + ["toileting"]

    # Move data to -0.5 so perfect behavior is 0
    data[facets_cols] = data[facets_cols]-0.5

    for col in facets_cols:
        left_col_name = col+"_LEFT"
        right_col_name = col+"_RIGHT"

        data[left_col_name] = np.where(data[col]<=0, -data[col], 0)
        data[right_col_name] = np.where((data[col]>=0), data[col], 0)

    data = data.drop(facets_cols, axis=1)

    return data

if __name__ == "__main__":
    
    facets_data = json.load(open("data/facets.json"))
    sdq_data = pd.read_csv("data/sdq.csv", sep=";")
    diagnostics_data = pd.read_csv("data/diagnostics.csv", sep=";")

    sdq_data = preprocess_sdq(sdq_data)
    facets_data = preprocess_facets(facets_data)
    diagnostics_data = preprocess_diagnostics(diagnostics_data)

    sdq_data = sdq_data.rename(columns={"anonymised ID": "Study ID"})
    
    sdq_data.to_csv("data/sdq_scored_cleaned.csv")
    facets_data.to_csv("data/facets_transformed.csv")
    diagnostics_data.to_csv("data/diagnostics_transformed.csv")

    sdq_grouped = sdq_data.groupby("Study ID", as_index=False).mean()
    facets_grouped = facets_data.drop([
        "Entry ID",
        "Actor type",
        "Group ID",
        "Time",
        "Subject-Respondent Pair ID",
        "Subject ID"], axis=1).groupby("Study ID", as_index=False).mean()
    # Take first entry for each participant (:TODO take senior value)
    diagnostics_grouped = diagnostics_data.groupby("Study ID").first()

    sdq_grouped.to_csv("data/sdq_scored_cleaned_grouped.csv")
    facets_grouped.to_csv("data/facets_transformed_grouped.csv")
    diagnostics_grouped.to_csv("data/diagnostics_transformed_grouped.csv")

    print(facets_grouped.columns)
    print(sdq_grouped.columns)
    print(diagnostics_grouped.columns)

    merged = sdq_grouped.merge(
        facets_grouped, 
        on="Study ID",
        how="inner")
    merged = merged.merge(
        diagnostics_grouped,
        on="Study ID",
        how="inner"
    )
    print(merged.describe())

    merged.to_csv("data/merged.csv")

    print("Unique Patient IDs in SDQ: ", len(sdq_grouped["Study ID"].unique()))
    print("Unique Patient IDs in FACETS: ", len(facets_grouped["Study ID"].unique()))
    print("Unique Patient IDs in Merged: ", len(merged["Study ID"].unique()))

    merged_grouped_and_split_by_anchor = split_by_anchor(merged)
    merged_grouped_and_split_by_anchor.to_csv("data/merged_split_by_anchor.csv")

    
