import os, glob, json, csv, re
from collections import defaultdict, Counter

def norm_country(c):
    if not c: return ''
    c = c.replace('_', ' ').strip()
    c_lower = c.lower()
    mapping = {
        'uk': 'United Kingdom',
        'united kingdom': 'United Kingdom',
        'bosnia': 'Bosnia and Herzegovina',
        'bosnia and herzegovina': 'Bosnia and Herzegovina',
        'uae': 'United Arab Emirates',
        'united arab emirates': 'United Arab Emirates',
        'us': 'United States',
        'usa': 'United States',
        'united states': 'United States',
        'dr congo': 'Democratic Republic of the Congo',
        'democratic republic of the congo': 'Democratic Republic of the Congo',
        'israel/palestine': 'Palestine',
        'czechia': 'Czech Republic',
        'burkina faso': 'Burkina Faso',
        'cape verde': 'Cabo Verde',
        'ivory coast': "Cote d'Ivoire",
        'côte d’ivoire': "Cote d'Ivoire",
        'bahrain': 'Bahrain',
        'benin': 'Benin'
    }
    return mapping.get(c_lower, c.title())

def clean_isbn(isbn):
    if not isbn: return ''
    s = re.sub(r'[^0-9X]', '', str(isbn).upper())
    if len(s) == 10:
        core = '978' + s[:-1]
        check = (10 - sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(core)) % 10) % 10
        return core + str(check)
    return s

def get_tokens(s):
    if not s: return set()
    s = str(s).lower()
    words = re.sub(r'[\W_]+', ' ', s).split()
    stop = {'the', 'of', 'and', 'in', 'a', 'an', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'de', 'del', 'la', 'el', 'en', 'et', 'und', 'der', 'die', 'das', 'le', 'les', 'du', 'des', 'editions', 'edition', 'translation', 'translations', 'quran', 'koran', 'corán', 'coran', 'alcorão', 'al', 'noble', 'holy', 'sagrado', 'saint', 'meaning', 'meanings', 'complete', 'first', 'second', 'new', 'official', 'part', 'vol', 'vols'}
    return set(w for w in words if w not in stop and len(w) > 2)

FIELDNAMES = [
    'country', 'mushaf_title', 'riwaya', 'script_style', 'calligrapher',
    'language', 'content_type', 'edition_number', 'publication_year',
    'isbn', 'pages', 'size', 'publisher_name', 'publisher_city',
    'publisher_country', 'publisher_website', 'publisher_type',
    'approval_body', 'confidence', 'accessed_on', 'source_urls'
]

# 1. Load AGY base
agy_list = list(csv.DictReader(open('AGY-results/master_utf8.csv', encoding='utf-8-sig')))
for r in agy_list:
    r['country'] = norm_country(r['country'])

# 2. Load GLM raw
glm_raw_list = []
glm_no_local_list = []
for f in glob.glob('glm-results/data/*.jsonl'):
    for l in open(f, encoding='utf-8'):
        if not l.strip(): continue
        d = json.loads(l)
        if d.get('content_type') == 'no_local_editions_found' or not d.get('mushaf_title'):
            glm_no_local_list.append(d)
        else:
            glm_raw_list.append(d)

# 3. Clean GLM records
glm_cleaned = []
excluded_non_mushaf = []
for d in glm_raw_list:
    item = dict(d)
    item['country'] = norm_country(item.get('country'))
    ct = str(item.get('content_type', '')).lower()
    
    if 'periodical' in ct or 'newspaper' in ct:
        excluded_non_mushaf.append(item)
        continue
        
    pub = item.get('publisher') or {}
    pub_name = pub.get('name') if isinstance(pub, dict) else ''
    isbn = item.get('isbn') or ''
    notes = item.get('notes') or ''
    
    # Fix Germany field inversion (ISBN in publisher_name)
    if pub_name and re.match(r'^(97[89][-\s]?)?[0-9]{1,5}[-\s]?[0-9]+[-\s]?[0-9]+[-\s]?[0-9X]$', str(pub_name).strip()):
        actual_isbn = str(pub_name).strip()
        actual_notes = isbn if isbn else notes
        if isinstance(pub, dict):
            pub['name'] = ''
        item['isbn'] = actual_isbn
        item['notes'] = actual_notes
        
    callig = item.get('calligrapher')
    if callig and any(k in str(callig) for k in ['Henning', 'Paret', 'Khoury', 'Karimi', 'Zirker', 'Rückert', 'Goldschmidt', 'Sadr ud-Din', 'Rassoul', 'Ullmann', 'Öngüt', 'Schweigger', 'Mirza Tahir', 'Abdullah ibn Abd al-Aziz']):
        item['notes'] = (item.get('notes') or '') + f' [Translator/Editor: {callig}]'
        item['calligrapher'] = None

    # Handle internal GLM duplicate: Czech Republic Levné knihy (2006 vs 2010 reprint, same ISBN 9788073099923)
    if item['country'] == 'Czech Republic' and clean_isbn(item.get('isbn')) == '9788073099923':
        existing = [x for x in glm_cleaned if x['country'] == 'Czech Republic' and clean_isbn(x.get('isbn')) == '9788073099923']
        if existing:
            existing[0]['publication_year'] = '2006 (reprinted 2010)'
            existing[0]['mushaf_title'] = 'Korán (Levné knihy KMa)'
            continue

    glm_cleaned.append(item)

# 4. Deduplication Matching Engine
matches = []
matched_agy = set()
matched_glm = set()

# Strategy A: Exact ISBN match
for gi, g in enumerate(glm_cleaned):
    g_isbn = clean_isbn(g.get('isbn'))
    if not g_isbn: continue
    g_c = g['country']
    for ai, a in enumerate(agy_list):
        if ai in matched_agy: continue
        if a['country'] != g_c: continue
        a_isbn = clean_isbn(a['isbn'])
        if a_isbn and a_isbn == g_isbn:
            matches.append((ai, gi, f'EXACT_ISBN ({a_isbn})'))
            matched_agy.add(ai)
            matched_glm.add(gi)
            break

# Strategy B: High-confidence domain specific matches
for gi, g in enumerate(glm_cleaned):
    if gi in matched_glm: continue
    g_c = g['country']
    g_title = str(g.get('mushaf_title') or '')
    g_tokens = get_tokens(g_title) | get_tokens(g.get('notes'))
    g_year = str(g.get('publication_year') or '')
    
    for ai, a in enumerate(agy_list):
        if ai in matched_agy: continue
        if a['country'] != g_c: continue
        
        a_title = str(a.get('mushaf_title') or '')
        a_tokens = get_tokens(a_title) | get_tokens(a.get('publisher_name'))
        a_year = str(a.get('publication_year') or '')
        
        reason = None
        if g_c == 'Algeria' and ('الجزائر' in g_title or 'warsh' in g_tokens) and ('الجزائر' in a_title or 'ورش' in a_title):
            reason = 'ALGERIA_NATIONAL_WARSH'
        elif g_c == 'Morocco' and ('الملكي' in g_title or 'mohammed' in g_tokens) and ('المحمدي' in a_title):
            reason = 'MOROCCO_ROYAL_WARSH'
        elif g_c == 'Japan' and ('井筒' in g_title or 'iwanami' in g_tokens) and ('iwanami' in a['publisher_name'].lower() or '9784003381311' in a['isbn']):
            reason = 'JAPAN_IZUTSU_IWANAMI'
        elif g_c == 'Japan' and ('三田' in g_title or 'mita' in g_tokens or '注解' in g_title) and ('三田' in a_title or 'mita' in a_tokens or '注解' in a_title):
            reason = 'JAPAN_UMAR_MITA'
        elif g_c == 'France' and 'hamidullah' in g_tokens and 'hamidullah' in a_tokens:
            reason = 'FRANCE_HAMIDULLAH'
        elif g_c == 'France' and 'masson' in g_tokens and 'masson' in a_tokens:
            reason = 'FRANCE_MASSON'
        elif g_c == 'Serbia' and 'korkut' in g_tokens and 'korkut' in a_tokens:
            reason = 'SERBIA_KORKUT'
        elif g_c == 'Serbia' and ('ljubibratić' in g_tokens or 'ljubibratic' in g_tokens) and ('ljubibratić' in a_tokens or 'ljubibratic' in a_tokens):
            reason = 'SERBIA_LJUBIBRATIC'
        elif g_c == 'Poland' and 'bielawsk' in g_title.lower() and ('bielawsk' in a_title.lower() or '8306011686' in a['isbn']):
            reason = 'POLAND_BIELAWSKI'
        elif g_c == 'Bosnia and Herzegovina' and 'korkut' in g_tokens and 'korkut' in a_tokens:
            reason = 'BOSNIA_KORKUT'
        elif g_c == 'Montenegro' and 'korkut' in g_tokens and 'korkut' in a_tokens:
            reason = 'MONTENEGRO_KORKUT'
        elif g_c == 'United Kingdom' and 'haleem' in g_tokens and 'haleem' in a_tokens:
            reason = 'UK_ABDEL_HALEEM'
        elif g_c == 'Spain' and 'melara' in g_tokens and 'melara' in a_tokens:
            reason = 'SPAIN_MELARA'
        elif g_c == 'Sweden' and ('bernström' in g_tokens or 'bernstrom' in g_tokens) and ('bernström' in a_tokens or 'bernstrom' in a_tokens):
            reason = 'SWEDEN_BERNSTROM'
        elif g_c == 'Estonia' and ('udam' in g_tokens or 'avita' in g_tokens) and ('udam' in a_tokens or 'avita' in a_tokens):
            reason = 'ESTONIA_UDAM_AVITA'
        elif g_c == 'Latvia' and ('bērziņš' in g_tokens or 'berzins' in g_tokens or 'bērziņa' in g_tokens) and ('bērziņš' in a_tokens or 'berzins' in a_tokens or 'bērziņa' in a_tokens):
            reason = 'LATVIA_BERZINS'
        elif g_c == 'Ukraine' and ('якубович' in g_title.lower() or 'osnovy' in g_tokens) and ('основи' in a['publisher_name'].lower() or '2015' in a_year):
            reason = 'UKRAINE_YAKUBOVYCH_OSNOVY'
        elif g_c == 'South Africa' and 'baker' in g_tokens and 'baker' in a_tokens:
            reason = 'SOUTH_AFRICA_BAKER'
        elif g_c == 'China' and ('jian' in g_tokens or '古兰经' in g_tokens) and ('jian' in a_tokens or '古兰经' in a_tokens):
            reason = 'CHINA_MA_JIAN'
        elif g_c == 'Bulgaria' and ('teofanov' in g_tokens or 'теофанов' in g_tokens) and ('teofanov' in a_tokens or 'теофанов' in a_tokens):
            reason = 'BULGARIA_TEOFANOV'
        elif g_c == 'Turkey' and 'diyanet' in g_tokens and 'diyanet' in a_tokens:
            reason = 'TURKEY_DIYANET'
        elif g_c == 'Indonesia' and ('2019' in g_year or 'penyempurnaan' in g_title.lower()) and ('2019' in a_year or '2019' in a_title):
            reason = 'INDONESIA_LPMQ_2019'
        elif g_c == 'Egypt' and ('amiriyya' in g_tokens or 'الأميري' in a_title or 'بولاق' in a_title) and ('amiriyya' in g_tokens or 'المصرية' in g_title):
            reason = 'EGYPT_AMIRIYYA'
        elif g_c == 'Saudi Arabia' and ('حفص' in a_title or '1984' in a_year) and ('مجمع الملك فهد' in g_title or 'المدينة' in g_title):
            reason = 'SAUDI_KFQPC_HAFS'
        elif g_c == 'Russia' and ('казанское' in a_title.lower() or '1803' in a_year) and ('kazan' in g_title.lower() or '1803' in g_title):
            reason = 'RUSSIA_KAZAN_1803'
        elif g_c == 'Russia' and ('кулиев' in a_title.lower() or 'kuliev' in a_title.lower()) and ('кулиев' in g_title.lower() or 'kuliev' in g_title.lower()):
            reason = 'RUSSIA_KULIEV'
        elif g_c == 'Romania' and 'grigore' in g_tokens and 'grigore' in a_tokens:
            reason = 'ROMANIA_GRIGORE'
        elif g_c == 'Norway' and 'berg' in g_tokens and 'berg' in a_tokens:
            reason = 'NORWAY_EINAR_BERG'
        elif g_c == 'Albania' and ('ahmeti' in g_tokens or 'sherif' in g_tokens) and ('ahmeti' in a_tokens or 'sherif' in a_tokens):
            reason = 'ALBANIA_AHMETI'
        elif g_c == 'Argentina' and ('abboud' in g_tokens or 'castellanos' in g_tokens or '1952' in g_year) and ('abboud' in a_tokens or '1953' in a_year or 'arábigo' in a['publisher_name'].lower()):
            reason = 'ARGENTINA_ABBOUD'
        elif g_c == 'Belarus' and '2021' in a_year and '2021' in g_year:
            reason = 'BELARUS_2021'
        elif g_c == 'Lithuania' and '2008' in a_year and '2008' in g_year:
            reason = 'LITHUANIA_2008'
        elif g_c == 'Hungary' and ('magyarországi' in g_tokens or 'muszlimok' in g_tokens) and ('magyarországi' in a_tokens or 'kegyes' in a_tokens):
            reason = 'HUNGARY_MME'

        if reason:
            matches.append((ai, gi, reason))
            matched_agy.add(ai)
            matched_glm.add(gi)
            break

print(f'Final Duplicate Pairs Detected & Merged: {len(matches)}')
print(f'Unique GLM Records Added: {len(glm_cleaned) - len(matched_glm)}')
print(f'Total Combined Master Records: {len(agy_list) + len(glm_cleaned) - len(matched_glm)}')

# 5. Build Combined Records List
combined_records = []
audit_log = []

agy_to_glm_match = {ai: (gi, reason) for ai, gi, reason in matches}

for ai, a in enumerate(agy_list):
    rec = dict(a)
    if ai in agy_to_glm_match:
        gi, reason = agy_to_glm_match[ai]
        g = glm_cleaned[gi]
        # Merge URLs
        a_urls = [u.strip() for u in (a.get('source_urls') or '').split(';') if u.strip()]
        g_urls = g.get('source_urls') or []
        if isinstance(g_urls, str): g_urls = [g_urls]
        all_urls = sorted(list(set(a_urls + [u.strip() for u in g_urls if u.strip()])))
        rec['source_urls'] = '; '.join(all_urls)
        
        # Fill in missing publisher website if available
        if not rec.get('publisher_website') and (g.get('publisher') or {}).get('website'):
            rec['publisher_website'] = g['publisher']['website']
            
        audit_log.append({
            'action': 'MERGED_DUPLICATE',
            'reason': reason,
            'country': rec['country'],
            'primary_title': rec['mushaf_title'],
            'duplicate_title': g.get('mushaf_title'),
            'primary_source': 'AGY',
            'merged_from': 'GLM'
        })
    else:
        audit_log.append({
            'action': 'KEPT_AGY_RECORD',
            'country': rec['country'],
            'title': rec['mushaf_title'],
            'primary_source': 'AGY'
        })
    combined_records.append(rec)

# Second, process unique GLM records
for gi, g in enumerate(glm_cleaned):
    if gi in matched_glm:
        continue
    
    pub = g.get('publisher') or {}
    pub_name = pub.get('name') if isinstance(pub, dict) else ''
    pub_city = pub.get('city') if isinstance(pub, dict) else ''
    pub_country = pub.get('country') if isinstance(pub, dict) else ''
    pub_website = pub.get('website') if isinstance(pub, dict) else ''
    pub_type = pub.get('type') if isinstance(pub, dict) else ''
    
    g_urls = g.get('source_urls') or []
    if isinstance(g_urls, list):
        urls_str = '; '.join(u.strip() for u in g_urls if u and u.strip())
    else:
        urls_str = str(g_urls)

    ct = str(g.get('content_type') or 'translation').strip()
    if 'mushaf' in ct.lower() and 'translation' in ct.lower():
        ct_norm = 'translation'
    elif 'mushaf' in ct.lower() and 'only' in ct.lower():
        ct_norm = 'mushaf only'
    elif 'translation' in ct.lower():
        ct_norm = 'translation'
    elif 'manuscript' in ct.lower():
        ct_norm = 'mushaf only'
    elif 'tafsir' in ct.lower():
        ct_norm = 'tafsir'
    else:
        ct_norm = 'translation'

    rec = {
        'country': g['country'],
        'mushaf_title': g.get('mushaf_title') or '',
        'riwaya': g.get('riwaya') or '',
        'script_style': g.get('script_style') or '',
        'calligrapher': g.get('calligrapher') or '',
        'language': g.get('language') or '',
        'content_type': ct_norm,
        'edition_number': str(g.get('edition_number') or ''),
        'publication_year': str(g.get('publication_year') or ''),
        'isbn': clean_isbn(g.get('isbn')),
        'pages': str(g.get('pages') or ''),
        'size': str(g.get('size') or ''),
        'publisher_name': str(pub_name or ''),
        'publisher_city': str(pub_city or ''),
        'publisher_country': str(pub_country or g['country']),
        'publisher_website': str(pub_website or ''),
        'publisher_type': str(pub_type or ''),
        'approval_body': str(g.get('approval_body') or ''),
        'confidence': str(g.get('confidence') or 'medium'),
        'accessed_on': str(g.get('accessed_on') or '2026-11-17'),
        'source_urls': urls_str
    }
    
    audit_log.append({
        'action': 'ADDED_UNIQUE_GLM_RECORD',
        'country': rec['country'],
        'title': rec['mushaf_title'],
        'primary_source': 'GLM'
    })
    combined_records.append(rec)

# Sort combined_records by country, publication_year
combined_records.sort(key=lambda x: (x['country'], x['publication_year'] or '9999', x['mushaf_title']))

# Save combined master CSVs
with open('combined_master.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(combined_records)

with open('combined_master_utf8.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(combined_records)

# Unify countries_ranked.csv
with open('AGY-results/countries_ranked.csv', 'r', encoding='utf-8-sig') as f:
    cr_records = list(csv.DictReader(f))

has_germany = any('german' in r['country'].lower() for r in cr_records)
if not has_germany:
    cr_records.append({
        'rank': '0',
        'country': 'Germany',
        'muslim_percentage': '6.6',
        'muslim_population': '5500000',
        'total_population': '84400000',
        'source_name': 'Federal Office for Migration and Refugees (BAMF) / Pew Research',
        'source_year': '2021',
        'source_url': 'https://www.bamf.de/EN/Themen/Forschung/Veroeffentlichungen/MuslimischesLebenDeutschland/muslimisches-leben-deutschland-node.html'
    })

cr_records.sort(key=lambda x: (float(x['muslim_percentage']), int(float(x.get('muslim_population', 0)))))
for i, r in enumerate(cr_records, start=1):
    r['rank'] = str(i)

with open('combined_countries_ranked.csv', 'w', encoding='utf-8-sig', newline='') as f:
    fieldnames = ['rank', 'country', 'muslim_percentage', 'muslim_population', 'total_population', 'source_name', 'source_year', 'source_url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cr_records)

# Create combined_data directory and write individual country jsonl files
os.makedirs('combined_data', exist_ok=True)

# Map editions by country
editions_by_country = defaultdict(list)
for r in combined_records:
    editions_by_country[r['country']].append(r)

# Map no-results from AGY and GLM
no_results_by_country = {}
for f in glob.glob('AGY-results/data/*.jsonl'):
    for l in open(f, encoding='utf-8'):
        if not l.strip(): continue
        d = json.loads(l)
        if d.get('status') == 'no_results':
            c = norm_country(d.get('country'))
            no_results_by_country[c] = d

for d in glm_no_local_list:
    c = norm_country(d.get('country'))
    if c not in no_results_by_country and c not in editions_by_country:
        no_results_by_country[c] = {
            'country': c,
            'status': 'no_results',
            'notes': d.get('notes') or f'No local printing documented for {c}; imports/gifts serve local Muslim community.',
            'searched_sources': d.get('source_urls') or [],
            'accessed_on': d.get('accessed_on') or '2026-11-17'
        }

# Write a jsonl for each ranked country
for cr in cr_records:
    c = cr['country']
    safe_name = c.replace(' ', '_').replace('/', '_')
    target_path = os.path.join('combined_data', f'{safe_name}.jsonl')
    with open(target_path, 'w', encoding='utf-8') as out_f:
        if c in editions_by_country:
            for ed in editions_by_country[c]:
                # Format edition object
                ed_obj = dict(ed)
                ed_obj['publisher'] = {
                    'name': ed_obj.pop('publisher_name', ''),
                    'city': ed_obj.pop('publisher_city', ''),
                    'country': ed_obj.pop('publisher_country', ''),
                    'website': ed_obj.pop('publisher_website', ''),
                    'type': ed_obj.pop('publisher_type', '')
                }
                out_f.write(json.dumps(ed_obj, ensure_ascii=False) + '\n')
        else:
            # write no_results
            nr_obj = no_results_by_country.get(c, {
                'country': c,
                'status': 'no_results',
                'notes': f'No verified local Quran printing documented for {c}. Community relies on imported editions.',
                'searched_sources': [],
                'accessed_on': '2026-11-17'
            })
            out_f.write(json.dumps(nr_obj, ensure_ascii=False) + '\n')

print(f'Wrote {len(cr_records)} country files in combined_data/ successfully!')

# Write audit log
with open('merge_audit_log.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_agy_editions': len(agy_list),
        'total_glm_raw_editions': len(glm_raw_list),
        'excluded_non_mushaf_periodicals': len(excluded_non_mushaf),
        'total_duplicates_merged': len(matches),
        'total_glm_unique_added': len(glm_cleaned) - len(matched_glm),
        'total_final_editions': len(combined_records),
        'duplicate_pairs': [
            {
                'country': agy_list[ai]['country'],
                'reason': reason,
                'agy_title': agy_list[ai]['mushaf_title'],
                'agy_year': agy_list[ai]['publication_year'],
                'agy_isbn': agy_list[ai]['isbn'],
                'glm_title': glm_cleaned[gi]['mushaf_title'],
                'glm_year': glm_cleaned[gi]['publication_year'],
                'glm_isbn': glm_cleaned[gi]['isbn']
            }
            for ai, gi, reason in matches
        ],
        'full_audit_log': audit_log
    }, f, ensure_ascii=False, indent=2)

print('Wrote merge_audit_log.json successfully!')

# 7. Split into mushaf_only and translations
for r in combined_records:
    if 'aljamiado' in r['mushaf_title'].lower() and r['country'] == 'Spain':
        r['content_type'] = 'translation'
    elif 'kitab tafsira' in r['mushaf_title'].lower() and r['country'] == 'Belarus':
        r['content_type'] = 'translation'
    elif r['content_type'] == 'tajweed':
        r['content_type'] = 'mushaf only'

mushaf_only_records = [r for r in combined_records if r['content_type'] == 'mushaf only']
translations_records = [r for r in combined_records if r['content_type'] != 'mushaf only']

# Add evidence_url to mushaf_only_records
evidence_map = {
    'Algeria': 'https://archive.org/details/MushafWarsh',
    'Austria': 'https://viewer.cbl.ie/viewer/image/Is_1431/1/LOG_0000/',
    'Bahrain': 'https://archive.org/details/20210325_20210325_0401',
    'Brunei': 'https://archive.org/details/20250510_20250510_0648',
    'Chad': 'https://archive.org/details/DORY3AMRMADINAHS',
    'China': 'https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E4%BC%8A%E6%96%AF%E5%85%B0%E6%95%99%E5%8D%8F%E4%BC%9A',
    'Egypt_Amiri': 'https://archive.org/details/way2sona_20160915_2156',
    'Egypt_Shamarly': 'https://archive.org/details/shamarlyshamarly',
    'India': 'https://archive.org/details/QuranMajeed-15Lines-PakistaniPrint',
    'Indonesia': 'https://archive.org/details/al-quran-kudus-30-juz',
    'Iran': 'https://archive.org/details/QuranofNeirizi',
    'Iraq': 'https://archive.org/details/1981_20260422',
    'Jordan': 'https://www.altafsir.com/Quran.asp',
    'Kuwait': 'https://archive.org/details/20200728_20200728_0545',
    'Lebanon_Tajweed': 'https://archive.org/details/Quran25',
    'Lebanon_Ilmiyah': 'https://archive.org/details/Al-QuranTadabburWaAmal',
    'Libya': 'https://archive.org/details/20240516_20240516_1544',
    'Malaysia': 'https://archive.org/details/mushaf-tajwid-beserta-terjemahan-ke-dalam-bahasa-malaysia',
    'Mauritania': 'https://play.google.com/store/apps/details?id=mr.quranwarch&hl=ar',
    'Morocco_Musabba': 'https://archive.org/details/Quran_Warsh_Moorocco',
    'Morocco_Mohammedi': 'https://pdf.quran.ws/pdfs/warsh/quran-warsh-mushaf.pdf',
    'Oman': 'https://mushafmuscat.om',
    'Pakistan': 'https://archive.org/details/AlQuranAlKareem16LinesTajCompany',
    'Palestine': 'https://archive.org/details/0590_20210109',
    'Qatar': 'https://archive.org/details/MushafQatar_20150445776437',
    'Russia': 'https://archive.org/details/006-qran-kazan-1803',
    'Saudi Arabia_Hafs': 'https://archive.org/details/MushafMadinaHafsGreen1441',
    'Saudi Arabia_Warsh': 'https://archive.org/details/ozkorallh_20181029_2220',
    'Senegal': 'https://archive.org/details/kamil_serigne_Fallou',
    'South Africa': 'https://aboutislam.net/muslim-issues/world/how-cape-town-muslims-saved-south-africas-oldest-quran/',
    'Sudan': 'https://archive.org/details/DORY3AMRMADINAHS',
    'Syria': 'https://ar.wikipedia.org/wiki/%D8%B9%D8%AB%D9%85%D8%A7%D9%86_%D8%B7%D9%87',
    'Tunisia': 'https://archive.org/details/qaloon_tunesCCCCCCCCCCCCCCCCCCCCC',
    'Turkey': 'https://archive.org/details/Hafizosman',
    'United Arab Emirates': 'https://archive.org/details/356835683586MAKTOOM',
    'Yemen': 'https://archive.org/details/A21_Almoshaf_Alcharif_Attributed_to_Ali_ben_Abi_Talib_The_copy_of_Sanaa'
}

def get_ev(country, title):
    if country == 'Egypt':
        if 'بولاق' in title or 'الأميري' in title: return evidence_map['Egypt_Amiri']
        if 'الشمرلي' in title: return evidence_map['Egypt_Shamarly']
    if country == 'Lebanon':
        if 'التجويد' in title: return evidence_map['Lebanon_Tajweed']
        if 'الكتب العلمية' in title: return evidence_map['Lebanon_Ilmiyah']
    if country == 'Morocco':
        if 'المسبع' in title: return evidence_map['Morocco_Musabba']
        if 'المحمدي' in title: return evidence_map['Morocco_Mohammedi']
    if country == 'Saudi Arabia':
        if 'ورش' in title: return evidence_map['Saudi Arabia_Warsh']
        if 'حفص' in title: return evidence_map['Saudi Arabia_Hafs']
    return evidence_map.get(country, '')

mushaf_fieldnames = list(FIELDNAMES)
title_idx = mushaf_fieldnames.index('mushaf_title')
mushaf_fieldnames.insert(title_idx + 1, 'evidence_url')

for r in mushaf_only_records:
    ev = get_ev(r['country'], r['mushaf_title'])
    r['evidence_url'] = ev
    sources = [u.strip() for u in (r.get('source_urls') or '').split(';') if u.strip()]
    if ev and ev not in sources:
        sources.insert(0, ev)
    r['source_urls'] = '; '.join(sources)

# Write mushaf_only.csv
with open('mushaf_only.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=mushaf_fieldnames)
    writer.writeheader()
    writer.writerows(mushaf_only_records)

with open('mushaf_only_utf8.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=mushaf_fieldnames)
    writer.writeheader()
    writer.writerows(mushaf_only_records)

# Write translations.csv
with open('translations.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(translations_records)

with open('translations_utf8.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(translations_records)

print(f'Wrote mushaf_only.csv ({len(mushaf_only_records)} records) and translations.csv ({len(translations_records)} records) successfully!')

