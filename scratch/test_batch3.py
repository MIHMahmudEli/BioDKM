import urllib.request, urllib.parse, json

TARGET_PUBS = ['Elsevier', 'Springer', 'IEEE', 'MDPI', 'Frontiers', 'Oxford', 'Nature', 'ACS', 'SAGE', 'Wiley']

def search_candidate(query):
    params = {
        'query.bibliographic': query,
        'filter': 'from-pub-date:2023-01-01,until-pub-date:2026-12-31,type:journal-article',
        'rows': 15,
        'select': 'DOI,title,author,container-title,volume,issue,page,article-number,published,publisher'
    }
    url = 'https://api.crossref.org/works?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'BioDKMResearch/1.0 (mailto:scholar@university.edu)'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data['message']['items']
            candidates = []
            for it in items:
                pub = it.get('publisher', '')
                year = it.get('published', {}).get('date-parts', [[None]])[0][0]
                doi = it.get('DOI', '')
                title = it.get('title', [''])[0]
                journal = it.get('container-title', [''])[0]
                authors = it.get('author', [])
                if not (year and year >= 2023 and doi and title and journal and authors):
                    continue
                matched_pub = any(tp.lower() in pub.lower() or tp.lower() in journal.lower() for tp in TARGET_PUBS)
                if matched_pub:
                    candidates.append({
                        'year': year, 'pub': pub, 'journal': journal, 'title': title,
                        'doi': doi, 'authors': authors, 'vol': it.get('volume', ''),
                        'iss': it.get('issue', ''), 'page': it.get('page', '') or it.get('article-number', '')
                    })
            return candidates
    except Exception as e:
        print(f"Error querying {query}: {e}")
        return []

queries = [
    ("ref21", "UMAP uniform manifold approximation projection biomedical single cell clustering"),
    ("ref22", "HDBSCAN density based clustering biomedical clinical data"),
    ("ref23", "TF-IDF text representation machine learning classification medical"),
    ("ref24", "K-means clustering algorithm biomedical health data"),
    ("ref25", "hierarchical clustering Ward linkage biomedical classification"),
    ("ref26", "Silhouette coefficient cluster validity index evaluation"),
    ("ref27", "Davies Bouldin index cluster validity evaluation unsupervised"),
    ("ref28", "topic coherence evaluation topic modeling NPMI")
]

for ref, q in queries:
    res = search_candidate(q)
    print(f"=== {ref} (query: {q}) ===")
    if res:
        c = res[0]
        print(f"[{c['year']}] {c['pub']} | {c['journal']}")
        print(f"Title: {c['title']}")
        print(f"DOI: {c['doi']}")
    else:
        print("NO MATCH")
