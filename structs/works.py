import imdb
import pandas as pd
from tsg.client import SyncTSGClient
from scrapers.storygraph import get_book
from scrapers.igdb import search_games, get_game
from sklearn.linear_model import LinearRegression

from structs.lib import Work, Library

db = imdb.Cinemagoer()
books = SyncTSGClient()


class Serializable:
    def serialize(self):
        self.serialized = True

    def get_episodes(self, data):
        self.seasons = data.get("seasons")

class PubWork(Work):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.genres=kwargs['genres']
        self.fandom=kwargs['fandom']
        self.serialized = False

    def get_fics(self):
        return get_works(self.fandom)
        return self.fics
        for id, data in self.fics.items():
            self.fics[id] = FanWork(
                title=data["title"],
                id=data['id'],
                date=data['date_updated'],
                author=data['authors'][0]['username'] if len(data['authors'])>0 else None,
                kudos=data['kudos'],
                warnings=data["warnings"],
                hits=data["hits"],
                characters=data["characters"],
                chapters=data['nchapters'],
                tags=data["tags"],
                fandoms=data["fandoms"],
                ships=data["relationships"],
                rating=data["rating"])

class ScreenWork(PubWork):
    
    search = db.search_movie

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        try:
            self.cast = kwargs["data"].get("cast")[0:10]
            self.writer = kwargs["data"].get("writers")[0]
        except TypeError:
            pass

    @staticmethod
    def identifier(data):
        return data.movieID

    @staticmethod
    def retrieve(data):
        id = ScreenWork.identifier(data)
        return db.get_movie(id)


class PageWork(PubWork):
    
    search=books.get_browse

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.reviews=kwargs['data'].get('reviews')
        self.rating=kwargs['data'].get('rating')
        self.edition=kwargs['data'].get('edition')
        self.genres=kwargs['data'].get('tags')
        
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
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.get_episodes(kwargs["data"])

class Podcast(Serializable, ScreenWork):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.get_episodes(kwargs["data"])


class Movie(ScreenWork):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class Book(PageWork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Comic(Serializable, PageWork):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class VideoGame(PubWork):
    
    search=search_games
    
    def __init__(self, *args, **kwargs):
        pass
                    
    @staticmethod
    def identifier(data):
        return data['id']
    
    @staticmethod
    def retrieve(data):
        id=VideoGame.identifier(data)
        return get_game(id)
