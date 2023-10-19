import imdb
from tsg.client import SyncTSGClient
from scrapers.ao3 import get_works
from scrapers.storygraph import get_book
from scrapers.igdb import search_games, get_game

db = imdb.Cinemagoer()
books = SyncTSGClient()

class WorkNotFoundError(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)

class Work(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self.title = kwargs["title"]
        self.id = kwargs["id"]
        self.date = kwargs['date']
        self.author = kwargs["author"]

    @staticmethod
    def search_by_name(func, params, kind=None):
        data = func(params)
        if data == None or len(data) == 0:
            raise WorkNotFoundError
        if kind=='book' or kind=='videogame' or not kind:
            return data[0]
        result = [d for d in data if Work.match_kind(kind, d)]
        if len(result) == 0:
            raise WorkNotFoundError
        return result[0]

    @staticmethod
    def match_kind(kind, data):
        return data.get("kind").__eq__(kind)


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
        self.fics = get_works(self.fandom)
        for id, data in self.fics.items():
            self.fics[id] = FanWork(
                title=data["title"],
                id=data['id'],
                date=data['date_updated'],
                author=data['authors'][0].username,
                kudos=data['kudos'],
                warnings=data["warnings"],
                hits=data["hits"],
                characters=data["characters"],
                chapters=data['nchapters'],
                tags=data["tags"],
                fandoms=data["fandoms"],
                ships=data["relationships"],
                rating=data["rating"])


class FanWork(Work):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.chapters = kwargs["chapters"]
        self.kudos = kwargs["kudos"]
        self.hits = kwargs["hits"]
        self.characters = kwargs["characters"]
        self.tags = kwargs["tags"]
        self.fandoms = kwargs["fandoms"]
        self.ships = kwargs["ships"]
        self.warnings = kwargs["warnings"]
        self.rating = kwargs["rating"]
        
    def approx_rating():
        # some algorithm to calculate how this work's kudos/views ratio compares to peer works
        # -- normalized, obviously
        pass


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
        super().__init__(self, *args, **kwargs)
        
                
    @staticmethod
    def identifier(data):
        return data['id']
    
    @staticmethod
    def retrieve(data):
        id=VideoGame.identifier(data)
        return get_game(id)
    
        
