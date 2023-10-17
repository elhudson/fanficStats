import imdb
from imdb import helpers

db = imdb.Cinemagoer()

from ao3_scraper import get_fandoms

fandoms = get_fandoms()
works = {"TV": fandoms["tvshows_fandoms.pkl"], "Movies": fandoms["movies_fandoms.pkl"]}

class WorkNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Work:
    def __init__(self, data):
        self.title = data.get("title")
        self.genres = data.get("genres")
        self.rating = {"average": data.get("rating"), "votes": data.get("votes")}
        self.date = data.get("year")
    @staticmethod
    def match_kind(kind, data):
        return data.get('kind').__eq__(kind)

class ScreenWork(Work):
    def __init__(self, data):
        try:
            self.cast = data.get("cast")[0:10]
            self.writer = data.get("writers")[0]
        except TypeError:
            pass
            
    @staticmethod
    def search_by_name(name, kind=None):
        data=db.search_movie(name)
        if data==None or len(data)==0:
            raise WorkNotFoundError(f"{name} was not found in IMDB's records.")
        if not kind:
            result=data[0]
        else:
            result=[d for d in data if Work.match_kind(kind, d)][0]
        if len(result)==0:
            raise WorkNotFoundError(f"{name} was not found in IMDB's records.")
        else:
            r=db.get_movie(result.movieID)
            return r



class PageWork(Work):
    def __init__(self, data):
        super().__init__(data)
        self.author = data.get("author")


class TV(ScreenWork):
    def __init__(self, data):
        super().__init__(data)
        self.seasons = data.get("seasons")
        self.date = {
            "start": data.get("year"),
            "end": data.get("series years").split("-")[1],
        }


class Movie(ScreenWork):
    def __init__(self, data):
        super().__init__(data)


class Book(PageWork):
    def __init__(self, data):
        super().__init__(data)

movies=[]
for w in works['Movies']:
    try:
        data=ScreenWork.search_by_name(w, kind='movie')
    except WorkNotFoundError:
        pass
    else:
        movies.append(Movie(data))
    