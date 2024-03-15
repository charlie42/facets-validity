import pandas as pd
import pingouin as pg

def filter_doubly_rated(df):
    # Filter participants rated by two clinicians
    df_check = df[["Study ID", "Respondent Hash"]]
    counts = df_check.groupby("Study ID").count() 
    twice = counts[counts["Respondent Hash"] == 2]
    double_rated_ids = list(twice.index.unique())

    df = df.set_index("Study ID")
    df = df.loc[double_rated_ids].reset_index("Study ID")

    return df

def get_rater_with_most_n(df):
    df = df[["Respondent Hash", "Study ID"]]
    respondent_counts = df.groupby("Respondent Hash").count()
    most_n = respondent_counts["Study ID"].max()
    rater_with_most_n = respondent_counts[respondent_counts["Study ID"] == most_n].index[0]
    print(rater_with_most_n)
    return rater_with_most_n

def filter_by_rater(df, raters):
    return df[(df["Respondent Hash"] == raters[0]) | (df["Respondent Hash"] == raters[1])]

def check_irr(df, facets_cols):
    rows = []
    for col in facets_cols:
        icc = pg.intraclass_corr(
            data=df, 
            targets="Study ID", 
            raters="Respondent Hash", 
            ratings=col).set_index('Type').loc["ICC1"][["ICC", "pval", "CI95%"]]
        rows.append([col, icc["ICC"], icc["pval"], icc["CI95%"]])
    icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
    icc_df.to_csv("output/paper/irr.csv", float_format='%.3f')
    return icc_df

if __name__ == "__main__":

    df = pd.read_csv("data/facets_transformed.csv", index_col=0)
    facets_cols = [x for x in df.columns if x not in [
        "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
    ]]

    df = filter_doubly_rated(df)
    print("DEBUG", len(df), len(df["Subject ID"].unique()), len(df["Study ID"].unique()))
    
    # Raters who rated most participants (from data_verification.py)
    raters = [
        "dd91d49eefa2c289c9eaef735967b4d5e659350f593678894250e5de1240f5a1d79073381fb49ccb6808b7a9d661603b9505ee26a10194d81a033aba9c06ebd0",
        "8f797962581e4e2c8607d89c848c8a6f82590b49e987e7df9fe444cbc313f7f6860820f4b6e0d9d1bbf8908b824d6b43d73fba2932e8af7e097ad2a83d7f35c1"
    ]
    df_for_irr = filter_by_rater(df, raters)

    icc_df = check_irr(df_for_irr, facets_cols)