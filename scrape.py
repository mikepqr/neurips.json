import bs4
import datetime as dt
import json
import requests

urlroot = "https://papers.nips.cc"


def get_abstract(url):
    page = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
    return page.find('p', 'abstract').text


def parse_bullet(bullet):
    paperurl = urlroot + bullet.find_next('a').attrs['href']
    abstract = get_abstract(paperurl)
    texts = [a.text for a in bullet.find_all('a')]
    return {'title': texts[0], 'authors': texts[1:], 'abstract': abstract}


def parse_page(source):
    page = bs4.BeautifulSoup(source, 'html.parser')
    papers = [parse_bullet(bullet)
              for bullet in page.find('div', 'main-container').find_all('li')]
    return papers


def parse_url(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.HTTPError as e:
        print(e)
        return []
    return parse_page(r.text)


def make_url(year):
    if year < 1987:
        raise ValueError("year must be 1987 or greater")
    if year == 1987:
        url = urlroot + "/book/neural-information-processing-systems-1987"
    else:
        number = year - 1987
        url = (urlroot +
               "/book/advances-in-neural-information-processing-systems" +
               "-{}-{}".format(str(number), str(year)))
    return url


def get_year(year):
    papers = parse_url(make_url(year))
    for paper in papers:
        paper['year'] = year
    return papers


def append_year(year):
    nips_year = get_year(year)
    with open('nips.json') as infile:
        nips_previous = json.loads(infile.read())
    return nips_previous + nips_year


def get_all_years():
    this_year = dt.datetime.now().year
    return sum([get_year(year) for year in range(1987, this_year + 1)], [])
