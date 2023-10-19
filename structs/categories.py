from scrapers.ao3 import get_fandoms
from structs.works import *

class Category:
    def __init__(self, name, key, kind, cls):
        self.name=name
        self.key=key
        self.kind=kind
        self.cls=cls
        
    def get_properties(self, fandoms):
        self.fandoms={f:None for f in fandoms[self.key]}
        
    def fetch_properties(self, testing=False):
        if not hasattr(self, 'fandoms'):
            self.get_properties(fandoms)
        iter=self.fandoms.keys()
        if testing:
            iter=list(iter)[0:10]
        for p in iter:
            try:
                data=Work.search_by_name(self.cls.search, p, kind=self.kind if hasattr(self, 'kind') else None)
            except WorkNotFoundError:
                continue
            else:
                full=self.cls.retrieve(data)
                self.fandoms[p]=self.cls(
                    genres=full.get('genres'),
                    title=full.get('title'),
                    fandom=p,
                    id=full.get('id'),
                    date=str(full.get('year')),
                    author=full.get('author'),
                    data=full)
        
fandoms = get_fandoms()
categories = {
    'TV':Category('TV', 'tvshows_fandoms.pkl', 'tv series', TV),
    'Movies':Category('Movies', 'movies_fandoms.pkl', 'movie', Movie),
    'Books':Category('Books', 'books_literature_fandoms.pkl', 'book', Book),
    'Games':Category('Games', 'videogames_fandoms.pkl', 'videogame', VideoGame)
}

