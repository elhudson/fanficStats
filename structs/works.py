import imdb
import pandas as pd
from tsg.client import SyncTSGClient
from scrapers.storygraph import get_book
from scrapers.igdb import search_games, get_game
from scrapers.ao3 import download_works, get_fandom_key
from sklearn.linear_model import LinearRegression

from structs.lib import Work, WorkNotFoundError
from structs.fanworks import FicLibrary

db = imdb.Cinemagoer()
books = SyncTSGClient()

class Serializable:
    def serialize(self):
        self.serialized = True

    def get_episodes(self, data):
        self.seasons = data.get("seasons")

class PubWork(Work):
    @classmethod
    def create(cls, data):
        base=cls.__mro__[1].create(data)
        base['fandom']=get_fandom_key(base['title'])
        return cls(base)
    
    @property        
    def fics(self):
        return FicLibrary.create(download_works(self['fandom']))
    
class ScreenWork(PubWork):
    search = db.search_movie
    @staticmethod
    def identifier(data):
        return data.movieID

    @staticmethod
    def retrieve(data):
        id = ScreenWork.identifier(data)
        return db.get_movie(id)


class PageWork(PubWork):
    search=books.get_browse
    @staticmethod
    def identifier(data):
        return data.id
    
    @staticmethod
    def retrieve(data):
        if not data:
            raise WorkNotFoundError
        id=PageWork.identifier(data)
        return get_book(id)

class TV(Serializable, ScreenWork):    
    @classmethod
    def create(cls, data):
        return cls(cls.__mro__[2].create(data.data))

class Podcast(Serializable, ScreenWork):
   pass

class Movie(ScreenWork):
   pass

class Book(PageWork):
    pass


class Comic(Serializable, PageWork):
    pass


class VideoGame(PubWork):
    search=search_games
                    
    @staticmethod
    def identifier(data):
        return data['id']
    
    @staticmethod
    def retrieve(data):
        id=VideoGame.identifier(data)
        return get_game(id)
