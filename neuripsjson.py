import json

import bs4
import modal
import requests

urlroot = "https://papers.nips.cc"

stub = modal.Stub(
    image=modal.Image.debian_slim().pip_install(
        "beautifulsoup4",
        "requests",
    ),
)


@stub.function()
def add_abstract_to_paper(paper):
    text = requests.get(paper["url"]).text
    page = bs4.BeautifulSoup(text, "html.parser")
    try:
        ps = page.find("h4", text="Abstract").find_next_siblings("p")
        abstract = "\n".join(p.text for p in ps).strip()
    except AttributeError:
        abstract = ""
    return {**paper, **{"abstract": abstract}}


def get_paper_from_li(bullet):
    titlelink = bullet.find_next("a")
    url = urlroot + titlelink.attrs["href"]
    title = titlelink.text
    authors = [a.strip() for a in bullet.find_next("i").text.split(",")]
    return {"title": title, "authors": authors, "url": url}


def get_papers_from_url(url):
    r = requests.get(url)
    r.raise_for_status()
    page = bs4.BeautifulSoup(r.text, "html.parser")
    papers = [
        get_paper_from_li(li)
        for li in page.find("div", "container-fluid").find_all("li")
    ]
    return papers


@stub.function()
def get_papers_for_year(year):
    papers = get_papers_from_url(f"{urlroot}/paper/{str(year)}")
    for paper in papers:
        paper["year"] = year
    return papers


def get_all_years():
    papers = sum(get_papers_for_year.map(range(1987, 2023)), [])
    papers = list(add_abstract_to_paper.map(papers))
    return papers


@stub.local_entrypoint()
def main():
    papers = get_all_years()
    with open("neurips.json", "w") as fp:
        json.dump(papers, fp, indent=2)
