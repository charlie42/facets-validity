import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt

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

def check_irr_icc(df, facets_cols, type, filename_suffix):
    rows = []
    for col in facets_cols:
        icc = pg.intraclass_corr(
            data=df, 
            targets="Study ID", 
            raters="Respondent Hash", 
            ratings=col).set_index('Type').loc[type][["ICC", "pval", "CI95%"]]
        rows.append([col, icc["ICC"], icc["pval"], icc["CI95%"]])
    icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
    icc_df.to_csv(f"output/paper/irr_{filename_suffix}.csv", float_format='%.3f')
    return icc_df

def check_irr_icc_fixed_raters(df, facets_cols):
    check_irr_icc(df, facets_cols, "ICC2", "fixed")

def check_irr_icc_random_raters(df, facets_cols):
    check_irr_icc(df, facets_cols, "ICC1", "random")

def bin(df, facets_cols, n_bins):
    # Bin FACETS cols into n_bins equally sized bins

    labels = range(0, n_bins)

    for col in facets_cols:
        new_name = col+"_binned"
        df[new_name] = pd.cut(df[col], bins=n_bins, labels=labels)

    return df

def add_rater_count_col(df):
    # Create a new column that counts raters per subject
    df["N Rater"] = df.groupby("Subject ID").cumcount()+1

    return df

def transform_for_percent_agreement(df, facets_cols, n_bins):
    # Bin into n bins
    binned = bin(df, facets_cols, n_bins) # Split FACETS responses into n bins
    
    return binned

def check_percentage_agreement(df, facets_cols):
    # Check absolute agreement

    rows = []

    for col in facets_cols:
        
        col_name = col+"_binned"
        
        # Check if two values for the subject are equal (1 unique value)
        agreement = df.groupby("Subject ID")[col_name].nunique().eq(1)
        agreement_percentage = agreement.sum()/len(agreement)
        
        # Calculate delta between respondes, non-binned values
        df[col] = pd.to_numeric(df[col], errors='coerce') # Is a cetegory now
        deltas = abs(df.groupby("Subject ID")[col].diff()) # Difference with previous row
        mean_delta = deltas.mean()

        # DEBUG
        if col == "other-special-issues_perception-of-reality":
            print(list(deltas))

        
        rows.append([col, agreement_percentage, mean_delta])

    result_df = pd.DataFrame(rows, columns=[
        "Item", 
        "Agreement Percentage", 
        "Mean difference (Score 0 to 1)"
    ])
    result_df.sort_values("Agreement Percentage", ascending=False).to_csv(
        "output/paper/agreement_percentage.csv",
        float_format='%.3f')

    return result_df

def transform_to_plot_agreeement(df, facets_cols):
    # Make dfs for several students, rows are items, 2 columns - 1 per rater
    students = df["Subject ID"].unique()[:3]
    print("Students plotted: ", students)

    dfs = []

    for student in students:

        student_df = df[df["Subject ID"] == student].T
        student_df.columns = ["Rater 1", "Rater 2"]

        dfs.append(student_df)

    return dfs

def plot_irr_student(df, id_for_filename, facets_cols):
    # Plot scatter with two values, 1 from each rater

    df = df.iloc[::-1] # Referse rows to plot vertically in the right direction

    ax = df.loc[facets_cols].reset_index().plot( # Need this to overlap to plots
        kind="scatter", 
        x="Rater 1", 
        y="index", 
        color="red",
        figsize=(6,10),
        alpha=0.5) # Half transparent dots
    df.loc[facets_cols].reset_index().plot(
        kind="scatter", 
        x="Rater 2", 
        y="index", 
        color="blue", 
        ax=ax,
        alpha=0.5)
    
    # Plot delta lines
    for item in df.loc[facets_cols].index:
        x1 = df.loc[item]["Rater 1"]
        x2 = df.loc[item]["Rater 2"]
        y1 = item
        y2 = item
        plt.plot([x1, x2], [y1, y2], color='k', linestyle='-', linewidth=2)
    
    for x in [0.1, 0.3, 0.5, 0.7, 0.9]: # Vertical grid
        plt.axvline(x=x, color='grey', linestyle='--') 
    
    plt.savefig(
        f"plots/irr_student_{id_for_filename}.png", 
        bbox_inches='tight', # To make y labels fit
        dpi=600) # Better resolution


def plot_agreement(df, facets_cols):
    dfs = transform_to_plot_agreeement(df, facets_cols)

    for i, df in enumerate(dfs):
        plot_irr_student(df, id_for_filename=i, facets_cols=facets_cols)
    

if __name__ == "__main__":

    df = pd.read_csv("data/facets_transformed.csv", index_col=0)
    facets_cols = [x for x in df.columns if x not in [
        "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
    ]]

    df = filter_doubly_rated(df)
    
    # Raters who rated most participants (from data_verification.py)
    raters = [
        "dd91d49eefa2c289c9eaef735967b4d5e659350f593678894250e5de1240f5a1d79073381fb49ccb6808b7a9d661603b9505ee26a10194d81a033aba9c06ebd0",
        "8f797962581e4e2c8607d89c848c8a6f82590b49e987e7df9fe444cbc313f7f6860820f4b6e0d9d1bbf8908b824d6b43d73fba2932e8af7e097ad2a83d7f35c1"
    ]
    df_for_irr = filter_by_rater(df, raters)

    icc_df = check_irr_icc_fixed_raters(df_for_irr, facets_cols)
    icc_df = check_irr_icc_random_raters(df, facets_cols)

    df_for_percent_agreement = bin(df, facets_cols, 5)
    check_percentage_agreement(df_for_percent_agreement, facets_cols)

    plot_agreement(df, facets_cols)