import AO3 as ao3
import os
from pathlib import Path
import pickle
import json
import numpy as np
import functools
from requests import RequestException
from datetime import datetime
import time
import pandas as pd
import backoff
from tqdm.notebook import tqdm
import math
import ast

from structs.lib import Library, Work

root_folder=Path(os.path.abspath(__file__)).parent.parent.__str__()
data_folder=os.path.join(root_folder, 'data/')

to_list=lambda x: ast.literal_eval(x)
to_int=lambda x: x
to_str=lambda x: str(x)
to_bool=lambda x: bool(x)

fic_fields={
    "id":to_str,
    "authors":to_str,
    "categories":to_list,
    "nchapters":to_int,
    "characters":to_list,
    "complete":to_bool,
    "date_updated":to_str,
    "fandoms":to_list,
    "hits":to_int,
    "comments":to_int,
    "kudos":to_int,
    "language":to_str,
    "rating":to_str,
    "relationships":to_list,
    "summary":to_str,
    "tags":to_list,
    "title":to_str,
    "warnings":to_list,
    "words":to_int,
    "expected_chapters":to_int,
    "bookmarks":to_int
}

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
    
def get_fandom_key(name):
    matches=[]
    for f in get_fandoms().values():
        for item in f:
            if item.find(name)!=-1:
                matches.append(item)
    counts=[]
    for m in matches:
        query=ao3.Search(fandoms=m)
        refresh(query)
        counts.append(query.total_results)
    fr=pd.DataFrame({'query':matches, 'results':counts}).sort_values(by='results')
    return fr.at[0, 'query']
        
@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def get_page(query, page):
    query.page=page
    refresh(query)
    return query.results

@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def download_works(fandom, num_works=False):
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
        download_page_range(fandom, query, get_page_range(progress, query, num_works=num_works))
        return load_works(fandom)

def get_page_range(progress, query, num_works=False):
    endpoint=math.floor(num_works/20) if num_works else query.pages+1
    return progress_bar(range(math.floor(progress/20)+1, endpoint))

def parse_works_chunk(works):
    data={f:[] for f in fic_fields.keys()}
    for fanfic in works:
        ff=fanfic.__dict__
        for list_name in data.keys():
            try:
                data[list_name].append(ff[list_name])
            except KeyError:
                data[list_name].append(None)
    return pd.DataFrame(data)


def download_page_range(fandom, query, rng):
    results=[]
    for p in progress_bar(rng, msg='Works downloaded'):
        results.extend(get_page(query, p))
        if p % 10 == 0:
            fr=parse_works_chunk(results)
            dump_works(fandom, fr)
            results=[]
    if len(results)>0:
        fr=parse_works_chunk(results)
        dump_works(fandom, fr)
    

def dump_works(fandom, works):
    name_transform=get_fandom_filename(fandom)
    needs_header=False
    if name_transform not in os.listdir(data_folder):
        open(os.path.join(data_folder, name_transform), 'w+').close()
        needs_header=True
    works.to_csv(os.path.join(data_folder, name_transform), mode='a', header=needs_header, index=False, sep='\t')
    
def load_works(fandom):
    name_transform=get_fandom_filename(fandom)
    if name_transform in os.listdir(data_folder):
        data=pd.read_csv(os.path.join(data_folder, name_transform), sep='\t', converters=fic_fields)
        data.columns = [x.lower() for x in data.columns]
    return pd.DataFrame()
    
def get_fandom_filename(fandom):
    return fandom.replace(' ', "_").lower()+'.tsv'

def get_num_works(fandom):
    query=ao3.Search(fandoms=fandom)
    refresh(query)
    return query.total_results

def get_by_property(*args, **kwargs):
    query=ao3.Search(*args, **kwargs)
    refresh(query)
    return query

