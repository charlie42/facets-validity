import pandas as pd 
import numpy as np

class SDQScorer():
    '''Takes a df with SDQ data, format:
    Columns: ID, consid, restles, somatic, ...
    Column names are from https://www.sdqinfo.org/c9.html
    Impact scores are not implemeted'''

    def __init__(self, df):
        self.df = df

    def _recode_inverse_items(self):
        recode_dict = {0: 2, 1: 1, 2: 0}
        
        self.df["obeys"].replace(recode_dict, inplace=True)
        self.df["reflect"].replace(recode_dict, inplace=True)
        self.df["attends"].replace(recode_dict, inplace=True)
        self.df["friend"].replace(recode_dict, inplace=True)
        self.df["popular"].replace(recode_dict, inplace=True)
        
    def _score_subscale(self, cols, name):
        df = self.df[cols]
        df["n missing"] = df.isnull().sum(axis=1) # Calculate nan values for each row
        df["score"] = df[cols].mean(axis=1, skipna=True) * 5
        df["score"] = np.round(df["score"])
        df[df["n missing"] > 3]["score"] = np.nan 
        print(df)
        self.df[name] = df["score"]

    def _score(self):

        # Score Emotion
        emo_cols = ["somatic", "worries", "unhappy", "clingy", "afraid"]
        emo_name = "emotion"
        self._score_subscale(emo_cols, emo_name)

        # Score Conduct
        conduct_cols = ["tantrum", "obeys", "fights", "lies", "steals"]
        conduct_name = "conduct"
        self._score_subscale(conduct_cols, conduct_name)

        # Score Hyper
        hyper_cols = ["restles", "fidgety", "distrac", "reflect", "attends"]
        hyper_name = "hyper"
        self._score_subscale(hyper_cols, hyper_name)

        # Score Peer 
        peer_cols = ["loner", "friend", "popular", "bullied", "oldbest"]
        peer_name = "peer"
        self._score_subscale(peer_cols, peer_name)

        # Score Prosoc
        prosoc_cols = ["consid", "shares", "caring", "kind", "helpout"]
        prosol_name = "prosoc"
        self._score_subscale(prosoc_cols, prosol_name)

        # Score total
        self.df["tot"] = (
            self.df[emo_name] + 
            self.df[conduct_name] + 
            self.df[hyper_name] + 
            self.df[peer_name]
        )

    def score(self):
        self._recode_inverse_items()
        self._score()

        return self.df
