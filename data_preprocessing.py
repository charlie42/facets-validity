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

if __name__ == "__main__":
    
    facets_data = json.load(open("data/facets.json"))
    sdq_data = pd.read_csv("data/sdq.csv", sep=";")

    sdq_data = preprocess_sdq(sdq_data)
    facets_data = preprocess_facets(facets_data)
    
    sdq_data.to_csv("data/sdq_scored_cleaned.csv")
    facets_data.to_csv("data/facets_transformed.csv")

    merged = sdq_data.merge(
        facets_data, 
        left_on="anonymised ID", 
        right_on="Study ID")
    print(merged.describe())

    merged.to_csv("data/merged.csv")

    print("Unique Patient IDs in SDQ: ", len(sdq_data["anonymised ID"].unique()))
    print("Unique Patient IDs in FACETS: ", len(facets_data["Subject ID"].unique()))
    print("Unique Patient IDs in Merged: ", len(merged["anonymised ID"].unique()))