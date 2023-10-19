import requests
from datetime import datetime
import json
from igdb.wrapper import IGDBWrapper
from exceptions import WorkNotFoundError

secret='tph3mopihr2eaemzo8cxu6sj8q04nc'
id='pul6qb90553a4bjzgauh14dywq71ke'
token=requests.post(f'https://id.twitch.tv/oauth2/token?client_id={id}&client_secret={secret}&grant_type=client_credentials').json()['access_token']

igdb=IGDBWrapper(client_id=id, auth_token=token)

def search_games(name):
    try:
        q=igdb.api_request('games', f'search "{name}"; limit 1;')
        return json.loads(q.decode('utf-8'))
    except requests.HTTPError:
        return []

def get_game(id):
    q=igdb.api_request('games', 
        f'''
            fields id, name, first_release_date, genres;
            where id = {id};
            limit 1;
        ''')
    refs=json.loads(q.decode('utf-8'))[0]
    for j in range(len(refs['genres'])):
        q=igdb.api_request('genres', f'fields id, name; where id={refs["genres"][j]}; limit 1;')
        refs['genres'][j]=json.loads(q.decode('utf-8'))[0]
    refs['year']=datetime.fromtimestamp(refs['first_release_date']).year
    refs['author']=None
    refs['title']=refs['name']
    return refs