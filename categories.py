from ao3_scraper import get_fandoms
from works import *

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
                data=Work.search_by_name(self.cls.search, p, kind=self.kind)
            except WorkNotFoundError:
                pass
            full=self.cls.retrieve(data)
            self.fandoms[p]=self.cls(
                title=full.get('title'),
                id=full.movieID,
                date=str(full.get('year')),
                author=full.get('writer'),
                data=full)
        
fandoms = get_fandoms()
categories = {
    'TV':Category('TV', 'tvshows_fandoms.pkl', 'tv series', TV),
    'Movies':Category('Movies', 'movies_fandoms.pkl', 'movie', Movie)
}