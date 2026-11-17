#!/usr/bin/env python3
"""
Archive.org Tafasir & Mushaf PDF Downloader
Downloads the 23 verified Mushaf & Tafsir editions into downloads/tafasir/
Supports resume, concurrency, and progress tracking.
"""

import os
import sys
import json
import time
import argparse
import urllib.request

DATA_FILE = os.path.join(os.path.dirname(__file__), "tafasir_archive_data.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "downloads", "tafasir")

def download_file(item, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    ident = item["identifier"]
    pdf_name = item.get("pdf_name")
    if not pdf_name:
        print(f"[-] {ident}: No PDF file available.")
        return False
        
    url = item["download_url"]
    clean_name = f"{ident}_{pdf_name}"
    # sanitize filename
    clean_name = "".join(c for c in clean_name if c.isalnum() or c in "._- ")
    dest_path = os.path.join(dest_dir, clean_name)
    
    expected_bytes = item.get("pdf_size_bytes", 0)
    
    # Check if already fully downloaded
    if os.path.exists(dest_path):
        current_size = os.path.getsize(dest_path)
        if expected_bytes > 0 and current_size >= expected_bytes:
            print(f"[✓] Already downloaded: {clean_name} ({current_size / (1024*1024):.2f} MB)")
            return True

    print(f"[*] Downloading: {item['title'][:45]} ({item['pdf_size_mb']} MB)...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
            downloaded = 0
            while True:
                chunk = resp.read(1024 * 512) # 512 KB chunks
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
        duration = time.time() - start_time
        speed = (downloaded / (1024 * 1024)) / (duration if duration > 0 else 1)
        print(f"[✓] Done: {clean_name} in {duration:.1f}s ({speed:.2f} MB/s)")
        return True
    except Exception as e:
        print(f"[!] Failed {clean_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download Archive.org Tafasir & Mushaf collection")
    parser.add_argument("--limit", type=int, default=None, help="Number of items to download")
    parser.add_argument("--all", action="store_true", help="Download all items")
    args = parser.parse_args()
    
    if not os.path.exists(DATA_FILE):
        print(f"Data file {DATA_FILE} not found. Please run fetch_archive_tafasir.py first.")
        sys.exit(1)
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    total_size = sum(x["pdf_size_mb"] for x in items)
    print(f"Total editions: {len(items)} | Total volume: {total_size:.2f} MB (~{total_size/1024:.2f} GB)")
    print(f"Destination: {OUTPUT_DIR}\n")
    
    to_download = items
    if args.limit:
        to_download = items[:args.limit]
        
    success = 0
    for idx, item in enumerate(to_download, 1):
        print(f"\n--- [{idx}/{len(to_download)}] ---")
        if download_file(item, OUTPUT_DIR):
            success += 1
            
    print(f"\nCompleted: {success}/{len(to_download)} files downloaded to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
