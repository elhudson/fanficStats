import AO3 as ao3
import os
from pathlib import Path
import pickle
import json
import functools
from requests import RequestException
from datetime import datetime
import time
import pandas as pd
import backoff
from tqdm.notebook import tqdm
import math
from structs.fanworks import FanWork
from structs.lib import Library

root_folder=Path(os.path.abspath(__file__)).parent.parent.__str__()
data_folder=os.path.join(root_folder, 'data/')


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
def get_page(query, page):
    query.page=page
    refresh(query)
    return [FanWork(d.__dict__) for d in query.results]

@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def download_works(fandom):
    name_transform=get_fandom_filename(fandom)  
    query=ao3.Search(fandoms=fandom)
    refresh(query)
    prev=load_works(fandom)
    if not prev.empty:
        progress=prev.shape[0]
    else:
        progress=0
    if progress>=query.total_results:
        return prev
    else:
        download_page_range(fandom, query, get_page_range(progress, query))
    

def get_page_range(progress, query):
    return progress_bar(range(math.floor(progress/20)+1, query.pages+1))

def download_page_range(fandom, query, rng):
    results=[]
    for p in progress_bar(rng, msg='Works downloaded'):
        results.extend(get_page(query, p))
        if p % 10 == 0:
            fr=Library.create(results)
            dump_works(fandom, fr)
            results=[]
    if len(results)>0:
        fr=Library.create(results)
        dump_works(fandom, fr)
    

def dump_works(fandom, works):
    name_transform=get_fandom_filename(fandom)
    if name_transform not in os.listdir(data_folder):
        open(os.path.join(data_folder, name_transform), 'w+').close()
    works.to_csv(os.path.join(data_folder, name_transform), mode='a')
    
def load_works(fandom):
    name_transform=get_fandom_filename(fandom)
    if name_transform in os.listdir(data_folder):
        dedupt=pd.read_csv(os.path.join(data_folder, name_transform), index_col='id').drop_duplicates(subset='title')
        dedupt.to_csv(os.path.join(data_folder, name_transform), mode='w+')
        return dedupt
    return pd.DataFrame()
    
def get_fandom_filename(fandom):
    return fandom.replace(' ', "_").lower()+'.csv'

def get_num_works(fandom):
    query=ao3.Search(fandoms=fandom)
    refresh(query)
    return query.total_results

def get_by_property(*args, **kwargs):
    query=ao3.Search(*args, **kwargs)
    refresh(query)
    return query

