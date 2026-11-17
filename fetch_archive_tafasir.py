import urllib.request
import urllib.parse
import json
import re
from concurrent.futures import ThreadPoolExecutor

SEARCH_URL = "https://archive.org/advancedsearch.php?q=subject%3A%22%D9%85%D8%B5%D8%A7%D8%AD%D9%81+%D9%88%D8%AA%D9%81%D8%A7%D8%B3%D9%8A%D8%B1%22&fl[]=identifier,title,description,creator,publicdate,year,downloads,item_size&rows=100&output=json"

def fetch_item_details(doc):
    ident = doc["identifier"]
    raw_title = doc.get("title", "")
    
    # Parse title & author if formatted with #
    # Example: "# قرآن كريم بتفسير الإمامين الجلالين (ط. الشمرلي) # المؤلف: جلال الدين المحلى # المحقق: ..."
    parts = [p.strip() for p in raw_title.split("#") if p.strip()]
    main_title = parts[0] if parts else raw_title
    author = doc.get("creator") or ""
    investigator = ""
    for p in parts[1:]:
        if "المؤلف:" in p or "المؤلف :" in p:
            author = p.replace("المؤلف:", "").replace("المؤلف :", "").strip()
        elif "المحقق:" in p or "المحقق :" in p:
            investigator = p.replace("المحقق:", "").replace("المحقق :", "").strip()
            
    files_url = f"https://archive.org/metadata/{ident}/files"
    req = urllib.request.Request(files_url, headers={"User-Agent": "Mozilla/5.0"})
    
    best_pdf = None
    all_pdfs = []
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            files_data = json.loads(resp.read().decode()).get("result", [])
            for f in files_data:
                fname = f.get("name", "")
                if fname.lower().endswith(".pdf") and not fname.endswith("_text.pdf"):
                    all_pdfs.append(f)
            
            # Select the largest or original PDF
            if all_pdfs:
                all_pdfs.sort(key=lambda x: int(x.get("size", 0)), reverse=True)
                best_pdf = all_pdfs[0]
    except Exception as e:
        print(f"Error fetching files for {ident}: {e}")

    pdf_name = best_pdf.get("name") if best_pdf else ""
    pdf_size_bytes = int(best_pdf.get("size", 0)) if best_pdf else 0
    pdf_size_mb = round(pdf_size_bytes / (1024 * 1024), 2)
    download_url = f"https://archive.org/download/{ident}/{urllib.parse.quote(pdf_name)}" if pdf_name else f"https://archive.org/details/{ident}"
    item_url = f"https://archive.org/details/{ident}"
    thumb_url = f"https://archive.org/services/img/{ident}"

    return {
        "identifier": ident,
        "title": main_title,
        "full_title": raw_title,
        "author": author,
        "investigator": investigator,
        "pdf_name": pdf_name,
        "pdf_size_mb": pdf_size_mb,
        "pdf_size_bytes": pdf_size_bytes,
        "download_url": download_url,
        "item_url": item_url,
        "thumb_url": thumb_url,
        "year": doc.get("year") or doc.get("publicdate", "")[:4],
        "downloads": doc.get("downloads", 0)
    }

def main():
    req = urllib.request.Request(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        docs = data.get("response", {}).get("docs", [])
    
    print(f"Found {len(docs)} records from archive.org query.")
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_item_details, docs))
        
    results.sort(key=lambda x: x["title"])
    
    with open("tafasir_archive_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed {len(results)} items into tafasir_archive_data.json")
    total_size = sum(x["pdf_size_mb"] for x in results)
    print(f"Total PDF volume: {total_size:.2f} MB (~{total_size/1024:.2f} GB)")
    for i, r in enumerate(results, 1):
        print(f"{i:2d}. {r['title'][:50]} | {r['author'][:30]} | {r['pdf_size_mb']} MB")

if __name__ == "__main__":
    main()
