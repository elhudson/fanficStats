import pandas as pd

class WorkNotFoundError(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)

class Work(pd.Series):        
    @property
    def _constructor(self):
        return Work

    @property
    def _constructor_expanddim(self):
        return Library
    
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
    
    @classmethod 
    def create(cls, data):
        if type(data) is not dict:
            data=data.__dict__
        return cls(data)


class Library(pd.DataFrame):
    @property
    def _constructor(self):
        return Library

    @property
    def _constructor_sliced(self):
        return Work
    
    