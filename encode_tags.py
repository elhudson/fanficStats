from structs.fanworks import FicLibrary
from scrapers.ao3 import fic_fields, to_list, load_works
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

def make_encoder():
    ofmd=FicLibrary.from_dataframe(load_works("Our Flag Means Death (TV)"))
    top_tags=ofmd.get_top_tags()
    encoder=np.zeros((len(ofmd), len(top_tags)))
    df=pd.DataFrame(data=encoder, columns=top_tags, index=False)
    df.to_csv("./encoder.tsv", sep="\t", index=False)
    
def get_encoder(enc_path):
    return pd.read_csv(enc_path, sep="\t")

