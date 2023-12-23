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

def make_encoder(samples):
    is_list=[s for s in samples.columns if type(samples.iloc[0][s])==list]
    for l in is_list:
        values=get_values(samples,l)
        encoder=np.zeros((len(samples), len(values)))
        for fic in range(len(encoder)):
            for attr in values:
                if attr in samples[l][fic]:
                    attr_index=np.where(values==attr)
                    fic_index=fic
                    encoder[fic_index][attr_index]=1
        return encoder