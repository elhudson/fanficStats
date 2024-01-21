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

root_folder = Path(os.path.abspath(__file__)).parent.parent.__str__()
data_folder = os.path.join(root_folder, "data/")


def avoid_ddos(func):
    @functools.wraps(func)
    def ad_wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)

    return ad_wrapper


def progress_bar(range, msg="Progress"):
    return tqdm(range, msg)


@avoid_ddos
def refresh(query):
    query.update()


def get_fandoms():
    resources = os.path.join(os.path.dirname(ao3.__file__), "resources/fandoms")
    if not os.path.exists(resources):
        for key, fandom in ao3.extra._FANDOM_RESOURCES.items():
            fandom()
    return {
        r: pickle.loads(open(os.path.join(resources, r), "rb").read())
        for r in os.listdir(resources)
    }


def get_fandom_key(name):
    matches = []
    for f in get_fandoms().values():
        for item in f:
            if item.find(name) != -1:
                matches.append(item)
    counts = []
    for m in matches:
        query = ao3.Search(fandoms=m)
        refresh(query)
        counts.append(query.total_results)
    fr = pd.DataFrame({"query": matches, "results": counts}).sort_values(by="results")
    return fr.at[0, "query"]


@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def get_page(query, page):
    query.page = page
    refresh(query)
    return query.results


@backoff.on_exception(backoff.expo, (RequestException, ao3.utils.HTTPError))
def download_works(fandom, num_works=False):
    query = ao3.Search(fandoms=fandom)
    refresh(query)
    prev = load_works(fandom)

    if not prev.empty:
        progress = prev.shape[0]
    else:
        progress = 0

    if progress >= query.total_results:
        return prev

    else:
        download_page_range(
            fandom, query, get_page_range(progress, query, num_works=num_works)
        )
        return load_works(fandom)


def get_page_range(progress, query, num_works=False):
    endpoint = math.floor(num_works / 20) if num_works else query.pages + 1
    return progress_bar(range(math.floor(progress / 20) + 1, endpoint))


def parse_works_chunk(works):
    fields = [
        "chapters",
        "id",
        "authors",
        "categories",
        "nchapters",
        "characters",
        "complete",
        "date_updated",
        "expected_chapters",
        "fandoms",
        "hits",
        "comments",
        "kudos",
        "language",
        "rating",
        "relationships",
        "restricted",
        "series",
        "summary",
        "tags",
        "title",
        "warnings",
        "words",
        "bookmarks",
    ]
    data = {f: [] for f in fields}
    works = [work.__dict__ for work in works]
    for w in works:
        for f in fields:
            if f in w.keys():
                data[f].append(w[f])
            else:
                data[f].append(None)
    return pd.DataFrame(data)


def download_page_range(fandom, query, rng):
    results = []
    for p in progress_bar(rng, msg="Works downloaded"):
        results.extend(get_page(query, p))
        if p % 10 == 0:
            fr = parse_works_chunk(results)
            dump_works(fandom, fr)
            results = []
    if len(results) > 0:
        fr = parse_works_chunk(results)
        dump_works(fandom, fr)


def dump_works(fandom, works):
    name_transform = get_fandom_filename(fandom)
    needs_header = False
    if name_transform not in os.listdir(data_folder):
        open(os.path.join(data_folder, name_transform), "w+").close()
        needs_header = True
    works.to_csv(
        os.path.join(data_folder, name_transform),
        mode="a",
        header=needs_header,
        index=False,
        sep="\t",
    )


def load_works(fandom):
    name_transform = get_fandom_filename(fandom)
    if name_transform in os.listdir(data_folder):
        data = pd.read_csv(
            os.path.join(data_folder, name_transform), sep="\t", converters=fic_fields
        )
        data.columns = [x.lower() for x in data.columns]
        return data
    return pd.DataFrame()


def get_fandom_filename(fandom):
    return fandom.replace(" ", "_").lower() + ".tsv"


def get_num_works(fandom):
    query = ao3.Search(fandoms=fandom)
    refresh(query)
    return query.total_results


def get_by_property(*args, **kwargs):
    query = ao3.Search(*args, **kwargs)
    refresh(query)
    return query
