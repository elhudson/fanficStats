import imdb
import pandas as pd
from structs.lib import Work, Library
from tsg.client import SyncTSGClient
from scrapers.storygraph import get_book
from scrapers.igdb import search_games, get_game
from sklearn.linear_model import LinearRegression

class FanWork(Work):
    def approx_rating(self):
        pass
    

class FicLibrary(Library):
    pass