import bs4
import datetime as dt
import requests

urlroot = "https://papers.nips.cc"

# Edit this to use pywren to speed up scraping of abstracts
use_pywren = False


def get_abstract(url):
    page = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
    return page.find('p', 'abstract').text


def add_abstract(paper):
    abstract = get_abstract(paper['url'])
    return {**paper, **{'abstract': abstract}}


def add_abstracts(papers):
    global use_pywren
    if use_pywren:
        print("pywren")
        import pywren
        pwex = pywren.default_executor()
        papers = pywren.get_all_results(pwex.map(add_abstract, papers))
    else:
        papers = [add_abstract(paper) for paper in papers]
    return papers


def parse_bullet(bullet):
    url = urlroot + bullet.find_next('a').attrs['href']
    texts = [a.text for a in bullet.find_all('a')]
    return {'title': texts[0], 'authors': texts[1:], 'url': url}


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
    year_url = make_url(year)
    papers = parse_url(year_url)
    for paper in papers:
        paper['year'] = year
    papers = add_abstracts(papers)
    return papers


def get_all_years():
    this_year = dt.datetime.now().year
    return sum([get_year(year) for year in range(1987, this_year + 1)], [])
