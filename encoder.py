import pandas as pd
import numpy as np

def get_values(samples, attr):
    s = []
    for d in samples[attr]:
        s.extend(d)
    tags = {t: s.count(t) for t in list(set(s))}
    counts = pd.DataFrame({attr: tags.keys(), "occurrences": tags.values()})
    if len(counts) > 500:
        return counts.loc[
            counts["occurrences"] >= np.percentile(counts["occurrences"], 99)
        ][attr].values.tolist()
    else:
        return counts[attr].values.tolist()
    
def make_single_encoder(fics, feature):
    samples=fics[feature]
    vals=list(set(samples.values))
    enc=np.zeros((len(samples), len(vals)))
    for f in range(len(fics)):
        for v in range(len(vals)): 
            if fics.iloc[f][feature]==vals[v]:
                enc[f][v]=1.0
    df=pd.DataFrame(data=enc, columns=vals)
    return df

def make_multi_encoder(fics, feature):
    values=get_values(fics,feature)
    encoder=np.zeros((len(fics), len(values)))
    for fic in range(len(encoder)):
        for attr in range(len(values)):
            if values[attr] in fics.iloc[fic][feature]:
                encoder[fic][attr]=1.0
    df=pd.DataFrame(data=encoder, columns=values)
    return df
