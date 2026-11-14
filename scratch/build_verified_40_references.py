import urllib.request, urllib.parse, json, time

SLOT_DOIS = {
    "ref1": "10.1016/j.compbiomed.2024.109623",
    "ref2": "10.1007/s11517-023-02934-8",
    "ref3": "10.1016/j.neucom.2024.129325",
    "ref4": "10.1038/s41598-026-76405-z",
    "ref5": "10.1016/j.artmed.2024.102889",
    "ref6": "10.1007/s41666-023-00157-y",
    "ref7": "10.1016/j.bj.2025.100868",
    "ref8": "10.1016/j.dib.2024.110418",
    "ref9": "10.1016/j.jbi.2024.104725",
    "ref10": "10.1038/s41597-025-05343-8",
    "ref11": "10.1093/bib/bbaf070",
    "ref12": "10.1093/bioadv/vbae194",
    "ref13": "10.1186/s13643-024-02470-y",
    "ref14": "10.1016/j.inffus.2024.102886",
    "ref15": "10.3389/frma.2023.1271385",
    "ref16": "10.1016/j.procs.2025.04.587",
    "ref17": "10.1109/access.2025.3552221",
    "ref18": "10.1016/j.procs.2026.07.058",
    "ref19": "10.1186/s12859-024-05928-x",
    "ref20": "10.1109/access.2025.3599722",
    "ref21": "10.1016/j.modpat.2026.101023",
    "ref22": "10.1016/j.jbi.2024.104732",
    "ref23": "10.1016/j.array.2025.100467",
    "ref24": "10.1016/j.jbi.2023.104544",
    "ref25": "10.1016/j.jbi.2025.104878",
    "ref26": "10.1016/j.patcog.2023.109910",
    "ref27": "10.1007/s10791-026-10094-0",
    "ref28": "10.1016/j.neucom.2025.132523",
    "ref29": "10.1016/j.jbi.2025.104958",
    "ref30": "10.1177/1759720X241308037",
    "ref31": "10.3389/ebm.2025.10389",
    "ref32": "10.3390/computation13060144",
    "ref33": "10.1016/j.jbi.2025.104825",
    "ref34": "10.1038/s41598-026-67679-4",
    "ref35": "10.1109/access.2024.3411717",
    "ref36": "10.1016/j.sapharm.2024.08.055",
    "ref37": "10.1109/access.2023.3266377",
    "ref38": "10.1016/j.neucom.2023.126453",
    "ref39": "10.1186/s40959-026-00520-z",
    "ref40": "10.1177/17474930261492876"
}

def clean_latex(text):
    text = text.replace('&amp;', '\\&').replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
    return text

def format_author(a):
    given = a.get('given', '').strip()
    family = a.get('family', '').strip()
    if not family:
        return given
    if not given:
        return family
    initials = '. '.join([p[0] for p in given.split() if p and p[0].isalpha()]) + '.'
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

def fetch_doi_metadata(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'BioDKMResearch/1.0 (mailto:scholar@university.edu)'})
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        msg = data['message']
        pub = msg.get('publisher', '')
        
        date_parts = msg.get('published-print', {}).get('date-parts') or \
                     msg.get('published-online', {}).get('date-parts') or \
                     msg.get('published', {}).get('date-parts') or [[None]]
        year = date_parts[0][0]
        
        title = msg.get('title', [''])[0].strip()
        journal = msg.get('container-title', [''])[0].strip()
        authors = msg.get('author', [])
        vol = msg.get('volume', '')
        iss = msg.get('issue', '')
        page = msg.get('page', '') or msg.get('article-number', '')
        
        return {
            'year': year, 'pub': pub, 'title': title, 'journal': journal,
            'authors': authors, 'vol': vol, 'iss': iss, 'page': page, 'doi': doi
        }

results = []
errors = []

for i in range(1, 41):
    key = f"ref{i}"
    doi = SLOT_DOIS[key]
    try:
        meta = fetch_doi_metadata(doi)
        year = meta['year']
        if not year or year < 2023:
            errors.append(f"{key}: invalid year {year}")
        
        authors_str = format_authors(meta['authors'])
        title_str = clean_latex(meta['title'])
        journal_str = clean_latex(meta['journal'])
        vol = meta['vol']
        iss = meta['iss']
        page = meta['page']
        
        vol_str = f"vol.~{vol}" if vol else ""
        iss_str = f"no.~{iss}" if iss else ""
        if page and ('-' in str(page) or '–' in str(page)):
            pp_str = f"pp.~{page.replace('–', '--')}"
        elif page:
            pp_str = f"Art. no.~{page}"
        else:
            pp_str = ""
            
        loc_parts = [p for p in [vol_str, iss_str, pp_str] if p]
        loc_str = ", ".join(loc_parts) + ", " if loc_parts else ""
        
        entry = f"\\bibitem{{{key}}} {authors_str}, ``{title_str},'' \\textit{{{journal_str}}}, {loc_str}{year}, doi: {doi}."
        results.append((key, year, meta['pub'], entry))
        print(f"[{i}/40] {key}: OK ({year}) | {meta['pub']}")
        time.sleep(0.05)
    except Exception as e:
        print(f"[{i}/40] {key}: FAILED - {e}")
        errors.append(f"{key}: {e}")

print("\n--- SUMMARY ---")
print(f"Successfully processed: {len(results)}/40")
if errors:
    print(f"Errors ({len(errors)}):", errors)
else:
    print("ALL 40 REFERENCES 100% VERIFIED! ZERO ERRORS!")

with open("scratch/verified_bibitems.tex", "w", encoding="utf-8") as f:
    for _, _, _, entry in results:
        f.write(entry + "\n\n")

print("Saved to scratch/verified_bibitems.tex")
