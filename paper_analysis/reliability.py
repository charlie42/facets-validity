import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
import itertools
from pathlib import Path

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

def check_irr_icc(df, facets_cols, raters_col, type):
    rows = []
    for col in facets_cols:
        icc = pg.intraclass_corr(
            data=df, 
            targets="Study ID", 
            raters=raters_col, 
            ratings=col).set_index('Type').loc[type][["ICC", "pval", "CI95%"]]
        rows.append([col, icc["ICC"], icc["pval"], icc["CI95%"]])
    icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
    #icc_df.to_csv(f"output/paper/irr_{filename_suffix}.csv", float_format='%.3f')
    return icc_df

def prepare_dfs_per_clinic(df):
    dfs = []

    clinicians = list(df["Respondent Hash"].unique())
    
    # Get all sets patients rated by the same 2 clinicians (=1 clinic)
    clinician_sets = list(itertools.combinations(clinicians, 2))

    for clinician_set in clinician_sets:
        sets_of_participants = []
        for clinician in clinician_set:
            participants_per_clinician = set(df[df["Respondent Hash"] == clinician]["Subject ID"].unique())
            sets_of_participants.append(participants_per_clinician)
        overlapping_participants = set.intersection(*sets_of_participants)
        if len(overlapping_participants) > 5:
            clinic_df = df[(df["Respondent Hash"].isin(clinician_set) & (df["Subject ID"].isin(overlapping_participants)))]
            dfs.append(clinic_df)
    
    return dfs

def check_icc_per_clinic(df, facets_cols):
    clinic_dfs = prepare_dfs_per_clinic(df)
    save_path = "output/paper/reliability/icc_per_clinic/"
    Path(save_path).mkdir(parents=True, exist_ok=True)

    for i, clinic_df in enumerate(clinic_dfs):
        icc_df = check_irr_icc_fixed_raters(clinic_df, facets_cols, "Respondent Hash")
        n = len(clinic_df["Subject ID"].unique())
        icc_df.to_csv(save_path+str(i)+"_"+str(n)+".csv", float_format='%.3f')

def prepare_df_across_clinics(df, facets_cols):
    df = add_rater_count_col(df)
    print(df.sort_values("Subject ID"))
    return df

def check_icc_across_clinics(df, facets_cols):
    df = prepare_df_across_clinics(df, facets_cols)
    icc_df = check_irr_icc_random_raters(df, facets_cols, raters_col="N Rater")
    
    icc_df.to_csv("output/paper/reliability/icc_across_clinics.csv", float_format='%.3f')
    
def check_irr_icc_fixed_raters(df, facets_cols, raters_col):
    return check_irr_icc(df, facets_cols, raters_col, "ICC2")

def check_irr_icc_random_raters(df, facets_cols, raters_col):
    return check_irr_icc(df, facets_cols, raters_col, "ICC1")

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
        "output/paper/reliability/agreement_percentage.csv",
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

    save_path = "output/paper/reliability/"
    Path(save_path).mkdir(parents=True, exist_ok=True)

    df = pd.read_csv("data/facets_transformed.csv", index_col=0)
    facets_cols = [x for x in df.columns if x not in [
        "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
    ]]

    df = filter_doubly_rated(df)
    
    check_icc_per_clinic(df, facets_cols)
    check_icc_across_clinics(df, facets_cols)

    df_for_percent_agreement = bin(df, facets_cols, 5)
    check_percentage_agreement(df_for_percent_agreement, facets_cols)

    plot_agreement(df, facets_cols)