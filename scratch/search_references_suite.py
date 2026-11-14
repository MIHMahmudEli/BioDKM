import urllib.request, urllib.parse, json, sys

TARGET_PUBS = ['Elsevier', 'Springer', 'IEEE', 'MDPI', 'Frontiers', 'Oxford', 'Nature']

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

def search_slot(query, key_name):
    params = {
        'query.bibliographic': query,
        'filter': 'from-pub-date:2023-01-01,until-pub-date:2026-12-31,type:journal-article',
        'rows': 10,
        'select': 'DOI,title,author,container-title,volume,issue,page,article-number,published,publisher'
    }
    url = 'https://api.crossref.org/works?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'BioDKMResearch/1.0 (mailto:scholar@university.edu)'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data['message']['items']
            for it in items:
                pub = it.get('publisher', '')
                year = it.get('published', {}).get('date-parts', [[None]])[0][0]
                doi = it.get('DOI', '')
                title = it.get('title', [''])[0]
                journal = it.get('container-title', [''])[0]
                authors = it.get('author', [])
                if not (year and year >= 2023 and doi and title and journal and authors):
                    continue
                # check if publisher matches target
                matched_pub = any(tp.lower() in pub.lower() or tp.lower() in journal.lower() for tp in TARGET_PUBS)
                if matched_pub:
                    authors_str = format_authors(authors)
                    vol = it.get('volume', '')
                    issue = it.get('issue', '')
                    page = it.get('page', '') or it.get('article-number', '')
                    
                    vol_str = f"vol.~{vol}" if vol else ""
                    iss_str = f"no.~{issue}" if issue else ""
                    pp_str = f"pp.~{page}" if page and '-' in str(page) else (f"Art. no.~{page}" if page else "")
                    
                    loc_parts = [p for p in [vol_str, iss_str, pp_str] if p]
                    loc_str = ", ".join(loc_parts) + ", " if loc_parts else ""
                    
                    entry = f"\\bibitem{{{key_name}}} {authors_str}, ``{title},'' \\textit{{{journal}}}, {loc_str}{year}, doi: {doi}."
                    print(f"FOUND for {key_name} [{pub}] ({year}):\n  {entry}\n")
                    return {
                        'key': key_name, 'pub': pub, 'year': year, 'journal': journal,
                        'title': title, 'doi': doi, 'entry': entry
                    }
    except Exception as e:
        print(f"Error for {key_name}: {e}")
    return None

if __name__ == '__main__':
    q = sys.argv[1]
    k = sys.argv[2]
    search_slot(q, k)
