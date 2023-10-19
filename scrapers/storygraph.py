from bs4 import BeautifulSoup
import requests
from tsg.client import SyncTSGClient


books=SyncTSGClient()

def get_book(id):
    url=books._book_handler.make_url(id)
    soup=BeautifulSoup(requests.get(url).text)
    title_author=soup.select_one('div.book-title-author-and-series')
    pub_data=[str.strip(''.join(d.text.split(':')[1::]))
         for d in soup.select('div.edition-info>p')]
    tag_selector='div.book-page-tag-section>span'
    year_selector='span.toggle-edition-info-link'
    review_selector='h3.community-reviews-heading a'
    rating_selector='span.average-star-rating'
    item={
            'title':str.strip(title_author.find('h3').text),
            'author':
                {
                    'name': str.strip(title_author.find('a').text),
                    'id':title_author.find('a').attrs['href'].split('/')[-1]
                },
            'id':id,
            'tags':[m.text for m in soup.select(tag_selector)] if soup.select_one(tag_selector) else [],
            'year':soup.select_one(year_selector).text.split()[-1] if soup.select_one(year_selector) else pub_data[4].split()[-1],
            'reviews':int(soup.select_one(review_selector).text.split()[0].replace(',', "")) if soup.select_one(review_selector) else None,
            'rating':float(soup.select_one(rating_selector).text.strip()) if soup.select_one(rating_selector) else None,
            'edition': {
                'isbn':pub_data[0],
                'format':pub_data[1],
                'language':pub_data[2],
                'publisher':pub_data[3],
                'date':pub_data[4]
            }
        }
    return item
    