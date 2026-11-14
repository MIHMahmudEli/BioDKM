import urllib.request, urllib.parse, json

TARGET_PUBS = ['Elsevier', 'Springer', 'IEEE', 'MDPI', 'Frontiers', 'Oxford', 'Nature', 'ACS', 'SAGE']

def format_author(a):
    given = a.get('given', '')
    family = a.get('family', '')
    if not family:
        return given
    if not given:
        return family
    initials = '. '.join([p[0] for p in given.split() if p]) + '.'
    return f"{initials} {family}"

def format_authors(author_list):
    if not author_list:
        return "Unknown"
    formatted = [format_author(a) for a in author_list]
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    elif len(formatted) > 6:
        return f"{formatted[0]}, {formatted[1]}, {formatted[2]}, \\textit{{et al.}}"
    else:
        return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"

def search_candidate(query, must_include=None):
    params = {
        'query.bibliographic': query,
        'filter': 'from-pub-date:2023-01-01,until-pub-date:2026-12-31,type:journal-article',
        'rows': 12,
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
                if must_include and not any(mi.lower() in title.lower() for mi in must_include):
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

# Test queries for batch 1 (ref2, ref3, ref4, ref5, ref7)
queries = [
    ("ref2", "MMBERT unified framework biomedical named entity recognition"),
    ("ref3", "transfer learning biomedical BERT text classification"),
    ("ref4", "multi-task learning biomedical text mining BERT"),
    ("ref5", "biomedical language models BERT transformers"),
    ("ref7", "large language models biomedical literature healthcare")
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
