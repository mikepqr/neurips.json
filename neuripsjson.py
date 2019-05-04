import datetime as dt
import json

import bs4
import requests

urlroot = "https://papers.nips.cc"

# Set this to True to use pywren to speed up scraping of abstracts
use_pywren = False

if use_pywren:
    import pywren
    from toolz.itertoolz import partition


def pywren_map_in_batches(fxn, args, batch_size=10):

    def batched_fxn(batch):
        return [fxn(b) for b in batch]

    pwex = pywren.default_executor()
    batches = partition(batch_size, args)
    return pwex.map(batched_fxn, batches)


def get_abstract(url):
    page = bs4.BeautifulSoup(requests.get(url).text, "html.parser")
    try:
        return page.find("p", "abstract").text
    except AttributeError:
        return ""


def add_abstract(paper):
    abstract = get_abstract(paper["url"])
    return {**paper, **{"abstract": abstract}}


def add_abstracts(papers):
    global use_pywren
    if use_pywren:
        futures = pywren_map_in_batches(add_abstract, papers, batch_size=10)
        papers = pywren.get_all_results(futures)
    else:
        papers = [add_abstract(paper) for paper in papers]
    return papers


def parse_bullet(bullet):
    url = urlroot + bullet.find_next("a").attrs["href"]
    texts = [a.text for a in bullet.find_all("a")]
    return {"title": texts[0], "authors": texts[1:], "url": url}


def parse_page(source):
    page = bs4.BeautifulSoup(source, "html.parser")
    papers = [
        parse_bullet(bullet)
        for bullet in page.find("div", "main-container").find_all("li")
    ]
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
        url = (
            urlroot
            + "/book/advances-in-neural-information-processing-systems"
            + "-{}-{}".format(str(number), str(year))
        )
    return url


def get_year(year):
    year_url = make_url(year)
    papers = parse_url(year_url)
    for paper in papers:
        paper["year"] = year
    papers = add_abstracts(papers)
    return papers


def get_all_years():
    this_year = dt.datetime.now().year
    return sum([get_year(year) for year in range(1987, this_year + 1)], [])


def load_and_append_year(year):
    with open('neurips.json') as infile:
        old_papers = json.load(infile)
    print("Loaded {} papers from neurips.json".format(len(old_papers)))
    new_papers = get_year(year)
    print("Added {} papers from {}".format(len(new_papers), year))
    return old_papers + new_papers
