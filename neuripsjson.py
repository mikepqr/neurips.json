import datetime as dt
import json

import bs4
import requests
from tqdm import tqdm

urlroot = "https://papers.nips.cc"


def get_abstract(url):
    page = bs4.BeautifulSoup(requests.get(url).text, "html.parser")
    try:
        ps = page.find("h4", text="Abstract").find_next_siblings("p")
        return "\n".join(p.text for p in ps).strip()
    except AttributeError:
        return ""


def add_abstract(paper):
    abstract = get_abstract(paper["url"])
    return {**paper, **{"abstract": abstract}}


def add_abstracts(papers):
    year = papers[0]["year"]
    papers = [add_abstract(paper) for paper in tqdm(papers, desc=str(year))]
    return papers


def parse_bullet(bullet):
    titlelink = bullet.find_next("a")
    url = urlroot + titlelink.attrs["href"]
    title = titlelink.text
    authors = [a.strip() for a in bullet.find_next("i").text.split(",")]
    return {"title": title, "authors": authors, "url": url}


def parse_page(source):
    page = bs4.BeautifulSoup(source, "html.parser")
    papers = [
        parse_bullet(bullet)
        for bullet in page.find("div", "container-fluid").find_all("li")
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


def get_year(year):
    papers = parse_url(f"{urlroot}/paper/{str(year)}")
    for paper in papers:
        paper["year"] = year
    papers = add_abstracts(papers)
    return papers


def get_all_years(last_year=None):
    if last_year is None:
        last_year = dt.datetime.now().year - 1
    years = [get_year(year) for year in range(1987, last_year + 1)]
    return sum(years, [])


def load_and_append_year(year):
    with open("neurips.json") as infile:
        old_papers = json.load(infile)
    print("Loaded {} papers from neurips.json".format(len(old_papers)))
    new_papers = get_year(year)
    print("Added {} papers from {}".format(len(new_papers), year))
    return old_papers + new_papers
