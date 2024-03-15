import pandas as pd

def print_stats(df):
    print(f"""{len(df)} FACETS entries,
          {len(df["Study ID"].unique())} participants, rated by
          {len(df["Respondent Hash"].unique())} clinicians""")
    
def how_many_rated_by_the_same_clinicians(df):
    # How many participants were rated by the same clinicans?
    clinicians = list(df["Respondent Hash"].unique())
    
    # Get all sets of n_teachers_overlep teachers out of all teachers
    import itertools
    clinician_sets = list(itertools.combinations(clinicians, 2))
    for clinician_set in clinician_sets:
        sets_of_participants = []
        for clinician in clinician_set:
            participants_per_clinician = set(data[data["Respondent Hash"] == clinician]["Subject ID"].unique())
            sets_of_participants.append(participants_per_clinician)
        overlapping_participants = set.intersection(*sets_of_participants)
        if len(overlapping_participants) > 0:
            print(f"{len(overlapping_participants)} participants are rated by 2 clinicians: ", clinician_set)

def check_for_irr(df):
    # Check that each participant was rated by two people
    df = df[["Study ID", "Respondent Hash"]]
    counts = df.groupby("Study ID").count()
    once = len(counts[counts["Respondent Hash"] == 1])
    twice = len(counts[counts["Respondent Hash"] == 2])
    more = len(counts[counts["Respondent Hash"] > 2])

    print(f"""{once} participants were rated by one clinician,
          {twice} participants were rated by two clinicians,
          {more} pariticipants were rated by more than 2 clinicians""")
    
    how_many_rated_by_the_same_clinicians(df)

if __name__ == "__main__":

    data = pd.read_csv("data/facets_transformed.csv", index_col=0)
    
    print_stats(data)
    check_for_irr(data)
