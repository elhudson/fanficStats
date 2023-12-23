import imdb
import pandas as pd
import numpy as np

from structs.lib import Work, Library
from scrapers.ao3 import download_works
from tsg.client import SyncTSGClient
from scrapers.storygraph import get_book
from scrapers.igdb import search_games, get_game
from sklearn.linear_model import LinearRegression

class FanWork(Work):
    def approx_rating(self):
        pass
    

class FicLibrary(Library):
    @staticmethod
    def create(fandom, num_works=False):
        works=download_works(fandom, num_works=num_works)
        return FicLibrary.from_dataframe(works)
        
    @staticmethod
    def from_dataframe(fr):
        fr.__class__=FicLibrary
        return fr
    
    def get_top_tags(self):
        s=[]
        for d in self['tags']:
            s.extend(d)
        tags={t:s.count(t) for t in list(set(s))}
        counts=pd.DataFrame({'tag':tags.keys(), 'occurrences':tags.values()})
        return counts.loc[counts['occurrences']>=np.percentile(counts['occurrences'], 99)]['tag'].values.tolist()