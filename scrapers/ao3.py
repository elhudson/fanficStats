import AO3 as ao3
import os
import pickle
import json
import functools
from requests import RequestException
from datetime import datetime
import time
import backoff
from tqdm.notebook import tqdm

def avoid_ddos(func):
    @functools.wraps(func)
    def ad_wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)
    return ad_wrapper

def progress_bar(range, msg='Progress'):
    return tqdm(range, msg)

class FicEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ao3.User) or isinstance(obj, ao3.Work) or isinstance(obj, ao3.Series):
            return obj.__dict__
        if isinstance(obj, datetime):
            return str(obj)
        return super().default(obj)

@avoid_ddos
def refresh(query):
    query.update()

def get_fandoms():
    resources=os.path.join(os.path.dirname(ao3.__file__), 'resources/fandoms')
    if not os.path.exists(resources):
        for key, fandom in ao3.extra._FANDOM_RESOURCES.items():
            fandom()
    return {
        r:pickle.loads(
            open(os.path.join(
                    resources, r), 
                 'rb').read()) 
        for r in os.listdir(resources)
        }

@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def get_works(fandom):
    results={}
    query=ao3.Search(fandoms=fandom)
    refresh(query)
    pages=range(1,query.pages+1)
    for p in progress_bar(pages, msg='Works downloaded'):
        data=get_page(query,p)
        for d in data:
            results[d['id']]=d
    return results

@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def get_page(query, page):
    query.page=page
    refresh(query)
    return [w.__dict__ for w in query.results]
        
def get_num_works(fandom):
    query=get_works(fandom)
    return query.total_results

def get_by_property(*args, **kwargs):
    query=ao3.Search(*args, **kwargs)
    refresh(query)
    return query

