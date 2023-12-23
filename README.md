# neurips.json

NeurIPS paper metadata in a json file (and the code to recreate and update that
file).

```python
>>> import json
>>> with open('neurips.json') as infile:
...     papers = json.load(infile)
>>> papers[5046]  # word2vec
{'title': 'Distributed Representations of Words and Phrases and their Compositionality',
 'authors': ['Tomas Mikolov',
  'Ilya Sutskever',
  'Kai Chen',
  'Greg S. Corrado',
  'Jeff Dean'],
 'url': 'https://papers.nips.cc/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html',
 'year': 2013,
 'abstract': 'The recently introduced continuous Skip-gram model is an efficient method for learning high-quality distributed vector representations that capture a large number of precise syntactic and semantic word relationships.  In this paper we present several improvements that make the Skip-gram model more expressive and enable it to learn higher quality vectors more rapidly.  We show that by subsampling frequent words we obtain significant speedup,  and also learn higher quality representations as measured by our tasks. We also introduce Negative Sampling, a simplified variant of Noise Contrastive Estimation (NCE) that learns more accurate vectors for frequent words compared to the hierarchical softmax.   An inherent limitation of word representations is their indifference to word order and their inability to represent idiomatic phrases.  For example, the meanings of Canada\'\' and "Air\'\' cannot be easily combined to obtain "Air Canada\'\'.  Motivated by this example, we present a simple and efficient method for finding phrases, and show that their vector representations can be accurately learned by the Skip-gram model. "'}
```

## pandas example

Load the data into a pandas DataFrame and find the number of papers by year:

```python
>>> import pandas as pd
>>> papers = pd.read_json('neurips.json')
>>> npapers = papers.groupby('year').size()
>>> print(npapers)
year
1987      90
1988      94
1989     101
[...]
2020    1898
2021    2334
2022    2834
dtype: int64
```

Find the average number of authors by year:

```python
>>> nauthors = papers['authors'].apply(len).groupby(papers['year']).mean()
>>> print(nauthors)
year
1987    1.966667
1988    2.372340
1989    2.257426
[...]
2020    4.104847
2021    4.255356
2022    4.654199
Name: authors, dtype: float64
```

Plot these:

```python
>>> import matplotlib.pyplot as plt
>>> fig, ax = plt.subplots(2, 1, sharex=True, figsize=(4, 3))
>>> ax[0] = npapers.plot(ax=ax[0])
>>> ax[0].set_ylabel('Papers')
>>> ax[0].set_ylim(0, None)
>>> ax[1] = nauthors.plot(ax=ax[1])
>>> ax[1].set_ylabel('Authors per paper')
>>> fig.savefig('plot.png', bbox_inches='tight')
```

![NeurIPS plot](plot.png)

## Recreate the json from scratch

`pip install httpx beautifulsoup4` then

```bash
$ python neuripsjson.py create  # ~5 minutes
```

## Append a year to existing json

```bash
$ python neuripsjson.py add 2021  # ~30 seconds
```
