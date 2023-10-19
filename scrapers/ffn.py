from __future__ import print_function
from tqdm.notebook import tqdm

import ffscraper as ffn

import backoff
import cloudscraper
from requests import RequestException
from bs4 import BeautifulSoup
import time

scraper=cloudscraper.create_scraper()
headers={
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Cookie':'''cookies=yes; cf_clearance=rBIfSxCxiZOGAeJNfUkKQ7Yzcp6jYTKTg7FgSJYaAFk-1697238930-0-1-93b8c405.6bf78340.4376c661-160.2.1697238930; __cf_bm=sSIN4JCPdHsohXxWBNQwxXJEYlyWndcQwrEFFWwYoaU-1697244554-0-AXcvdlF0LkYdIDkCn/JzyKjkULrFQduhOf/tGz4V9b1SwJHT3W8A15Ec1u9wkqVd2bE7n+tI6f/91XcdiZC2M6w='''
}

def ffn_url(a):
    url='https://www.fanfiction.net'
    return f'{url}{a["href"]}'

def get_categories(scraper=scraper):
    soup=get_page('https://www.fanfiction.net', scraper=scraper)
    hrefs=soup.find_all(id='gui_table1i')[0].find_all('a')
    return [ffn_url(h) for h in hrefs if 'crossovers' not in h['href']]

def get_fandoms(category_url, scraper=scraper):
    page=get_page(category_url, scraper=scraper)
    fandoms=page.find(id='list_output').find_all('a')
    return [ffn_url(h) for h in fandoms]

def get_works(fandom_url, scraper=scraper):
    page=get_page(fandom_url, scraper=scraper)
    ids=get_ids(page)
    for i in ids:
        page=get_page('https://fanfiction.net/s/'+i)
        data=get_data(page)
            
import requests

@backoff.on_exception(backoff.expo, RequestException)
def get_page(url, scraper=scraper):
    request=requests.get(url, headers=headers)
    print(request.status_code)
    if request.status_code != 200:
        raise RequestException
    else:
        return BeautifulSoup(request.content)

def get_ids(soup):
    stories = soup.find_all('a', {'class': 'stitle'}, href=True)
    sids = []
    for h in stories:
        sids.append(h['href'].split('/')[2])
    return sids

def num_pages(soup):
    number_of_pages = 0
    for center_tag in soup.find_all('center'):
        for a_tag in center_tag.find_all('a'):
            if 'Last' in a_tag:
                number_of_pages = int(a_tag['href'].split('=')[-1])
                break
    return number_of_pages

def scrape(url, scraper=scraper):
    soup = get_page(url)
    number_of_pages = num_pages(soup)
    sids = []
    if number_of_pages:
        for page in tqdm(range(1, number_of_pages+1)):
            sids += get_ids(get_page(url + '?&p=' + str(page), scraper=scraper))
    else:
        sids = get_ids(get_page(url, scraper=scraper))
    return sids


def _category_and_fandom(soup):
    """
    .. versionadded:: 0.3.0

    Returns the FanFiction category and fandom from the soup.

    * Category is one of nine possible categories from ``['Anime/Manga',
      'Books', 'Cartoons', 'Comics', 'Games', 'Misc', 'Movies',
      'Plays/Musicals', 'TV']``
    * Fandom is the specific sub-category, whereas category may be
     ``Plays/Musicals``, the fandom could be ``RENT``, ``Wicked``, etc.

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: Tuple where the first item is the category and the second item is
              the fandom.
    :rtype: tuple.

    .. code-block:: python

                    from ffscraper.fanfic.story import __category_and_fandom
                    from bs4 import BeautifulSoup as bs
                    import requests

                    r = requests.get('https://www.fanfiction.net/s/123')
                    html = r.text
                    soup = bs(html, 'html.parser')

                    print(_category_and_fandom(soup))

    .. code-block:: bash

                    ('Plays/Musicals', 'Wicked')
    """

    c_f = soup.find('div', {'id': 'pre_story_links'}).find_all('a', href=True)
    return c_f[0].text, c_f[1].text


def _not_empty_fanfic(soup):
    """
    .. versionadded:: 0.3.0

    Returns false if FanFiction.Net returns a 'Story Not Found' Exception
    (Story Not Found: Unable to locate story. Code 1.)

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: True if the story does not exist. False otherwise.
    :rtype: bool
    """

    empty = soup.find('span', {'class': 'gui_warning'})
    return not empty


def _timestamps(soup):
    """
    .. versionadded:: 0.3.0

    'Publication' and 'last updated' are two available timestamps.
    If only one timestamp is listed, the story's update and publication time
    should be the same.

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: Tuple where the first item is the publication time and the second
              item is the update time.
    :rtype: tuple
    """

    metadata_html = soup.find('span', {'class': 'xgray xcontrast_txt'})

    timestamps = metadata_html.find_all(attrs={'data-xutime': True})

    # Logic for dealing with the possibility that only one timestamp exists.
    if len(timestamps) == 1:
        when_updated = timestamps[0]['data-xutime']
        when_published = when_updated
    else:
        when_updated = timestamps[0]['data-xutime']
        when_published = timestamps[1]['data-xutime']

    return when_published, when_updated


def _title(soup):
    """
    .. versionadded:: 0.3.0

    Returns the fanfic's title from the soup.

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: The title of the fanfic as a string.
    :rtype: str.

    .. code-block:: python

                    from ffscraper.fanfic.story import _title
                    from bs4 import BeautifulSoup as bs
                    import requests

                    r = requests.get('https://www.fanfiction.net/s/123')
                    html = r.text
                    soup = bs(html, 'html.parser')

                    print(_title(soup))

    .. code-block:: bash

                    'There Once was a Man from Gilneas'
    """
    return soup.find('b', {'class': 'xcontrast_txt'}).text

def _metadata(soup):
    """
    .. versionadded:: 0.3.0

    Parses the metadata displayed on a page.

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: A dictionary of metadata.
    :rtype: dict.
    """

    metadata_html = soup.find('span', {'class': 'xgray xcontrast_txt'})
    metadata = metadata_html.text.replace('Sci-Fi', 'SciFi')
    metadata = [s.strip() for s in metadata.split('-')]
    return metadata


def _get_abstract_text(soup):
    """
    .. versionadded:: 0.3.0

    Returns the abstract for the story (short summary at the top of the page).

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: The abstract for the story.
    :rtype: str.
    """
    return soup.find('div', {'class': 'xcontrast_txt'}).text


def _get_story_text(soup):
    """
    .. versionadded:: 0.3.0

    Returns the story text from the page, identified by <div id='storytext'>

    .. note:: Particularly with older stories, this appears to fail
              occasionally. Alternatives or a regex-based method may be
              necessary at some point.

    :param soup: Soup containing a page from FanFiction.Net
    :type soup: bs4.BeautifulSoup class

    :returns: The story text as a string.
    :rtype: str.
    """
    return soup.find('div', {'id': 'storytext'}).text