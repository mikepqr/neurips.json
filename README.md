# nips.json

NIPS paper metadata in a json file (and code to generate the file)

```python
>>> import json
>>> with open('nips.json') as infile:
...     nips = json.loads(infile.read())
>>> nips[5165]  # word2vec
{'abstract': 'The recently introduced continuous Skip-gram model is an efficient method for learning high-quality distributed vector representations that capture a large number of precise syntactic and semantic word relationships.  In this paper we present several improvements that make the Skip-gram model more expressive and enable it to learn higher quality vectors more rapidly.  We show that by subsampling frequent words we obtain significant speedup,  and also learn higher quality representations as measured by our tasks. We also introduce Negative Sampling, a simplified variant of Noise Contrastive Estimation (NCE) that learns more accurate vectors for frequent words compared to the hierarchical softmax.   An inherent limitation of word representations is their indifference to word order and their inability to represent idiomatic phrases.  For example, the meanings of Canada\'\' and "Air\'\' cannot be easily combined to obtain "Air Canada\'\'.  Motivated by this example, we present a simple and efficient method for finding phrases, and show that their vector representations can be accurately learned by the Skip-gram model. "',
 'authors': ['Tomas Mikolov',
  'Ilya Sutskever',
  'Kai Chen',
  'Greg S. Corrado',
  'Jeff Dean'],
 'title': 'Distributed Representations of Words and Phrases and their Compositionality',
 'year': 2013}
```

## Example

Get number of papers:

```python
>>> import pandas as pd
>>> nips = pd.read_json('nips.json')
>>> npapers = nips.groupby('year').size()
```

Get average number of authors by year:

```python
>>> nauthors = nips['authors'].apply(len).groupby(nips['year']).mean()
```

Plot:

```python
>>> import matplotlib.pyplot as plt
>>> import seaborn
>>> fig, ax = plt.subplots(2, 1, sharex=True, figsize=(4, 3))
>>> ax[0] = npapers.plot(ax=ax[0])
>>> ax[0].set_ylabel('Papers')
>>> ax[1] = nauthors.plot(ax=ax[1])
>>> ax[1].set_ylabel('Authors per paper')
>>> fig.savefig('plot.png', bbox_inches='tight')
```

![nipsplot](plot.png)

## Recreate json from scratch

`pip install requests beautifulsoup4` then

```python
>>> import json
>>> import scrape
>>> nips = scrape.get_all_years()  # 30-60m on a fast connection
>>> with open('nips.json', 'w') as outfile:
...     json.dump(nips, outfile)
```

## Append a year to existing json

```python
>>> nips = append_year(2017)
>>> with open('nips.json', 'w') as outfile:
...     json.dump(nips, outfile)
```
