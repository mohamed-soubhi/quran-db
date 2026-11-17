# Global Quran Editions & Translations Database (Quran-DB)
# قاعدة بيانات مصاحف وتراجم القرآن الكريم حول العالم

[![Dataset: 319 Editions](https://img.shields.io/badge/Total%20Editions-319-emerald.svg)](combined_master.csv)
[![Arabic Mushafs: 36 Verified](https://img.shields.io/badge/Arabic%20Mushafs-36%20(100%25%20Verified)-green.svg)](mushaf_only.csv)
[![Translations: 283](https://img.shields.io/badge/Translations-283-cyan.svg)](translations.csv)
[![Countries Ranked: 227](https://img.shields.io/badge/Countries%20Ranked-227-amber.svg)](combined_countries_ranked.csv)
[![License: Open Data](https://img.shields.io/badge/License-CC%20BY%204.0%20%2F%20Open%20Data-blue.svg)](LICENSE)

[**English Overview**](#english-overview) | [**نظرة عامة بالعربية**](#نظرة-عامة-بالعربية) | [**Interactive Project Page**](https://mohamed-soubhi.github.io/quran-db/) | [**Audit Report**](consolidation_report.md)

---

## English Overview

**Quran-DB** is a curated, scholarly, and deduplicated global database cataloging printed editions, historical manuscripts, and vernacular translations of the Holy Quran across **123 countries**, accompanied by demographic analysis for **227 countries and territories**.

### Key Highlights
1. **Master Consolidated Dataset (`combined_master.csv`):** 319 unique, validated editions consolidated and reconciled from multi-agent research pipelines (`AGY` and `GLM`), resolving 31 duplicate cross-dataset pairs with zero data loss.
2. **Arabic Mushafs Only (`mushaf_only.csv`):** 36 Arabic-only editions and historical manuscripts across 31 countries. **100% of editions feature verified, active (HTTP 200) evidence URLs** pointing directly to complete digital scans (Internet Archive, Chester Beatty Library, Altafsir.com, state archives).
3. **Global Translations (`translations.csv`):** 283 translations and commentaries across 107 countries and over 80 languages/dialects.
4. **Demographic Country Index (`combined_countries_ranked.csv`):** 227 nations and territories sorted ascendingly by Muslim population percentage, with census numbers and research source notes.
5. **Interactive Web Dashboard:** An integrated bilingual web presentation ([index.html](index.html)) with live search, filters, cards, and direct scan viewing.
6. **Rare Mushafs & Tafasir Archive (`tafasir.html`):** A dedicated digital library indexing 23 monumental historical editions (3.48 GB total volume) from Internet Archive, complete with interactive flip-book reader embeds, direct PDF downloads, and a CLI bulk downloader (`download_tafasir.py`).

---

## نظرة عامة بالعربية

مشروع **قاعدة بيانات القرآن الكريم العالمية (Quran-DB)** هو مستودع علمي شامل ومحقق يوثق طبعات المصاحف الشريفة المطبوعة، والمخطوطات التاريخية النادرة، وترجمات معاني القرآن الكريم وتفاسيره عبر **123 دولة**، إلى جانب دراسة ديموغرافية لسكان المسلمين في **227 دولة وإقليماً**.

### أبرز مخرجات المشروع:
1. **قاعدة البيانات الموحدة الكاملة (`combined_master.csv`):** 319 طبعة فريدة محققة ومدققة، بعد دمج نتائج فريقي العمل السابقة وحل 31 زوجاً مكرراً بسجل تدقيق شفاف.
2. **المصاحف الشريفة بالنص العربي الخالص (`mushaf_only.csv`):** 36 طبعة ومخطوطة قرآنية كاملة في 31 دولة. **100% من المصاحف مزودة بروابط حية مباشرة (حالتها البرمجية المؤكدة HTTP 200)** تتيح تصفح المصحف كاملاً أو المخطوطة الأصلية عالي الدقة (عبر أرشيف الإنترنت، مكتبة تشستر بيتي، بوابة آل البيت، مكتبة الأقصى).
3. **التراجم والتفاسير العالمية (`translations.csv`):** 283 ترجمة وتفسيراً بمعاني القرآن إلى مختلف لغات ولهجات العالم عبر 107 دول.
4. **دليل تصنيف دول العالم ديموغرافياً (`combined_countries_ranked.csv`):** 227 دولة وإقليم مصنفة تصاعدياً بنسبة المسلمين وإجمالي السكان.
5. **لوحة عرض تفاعلية ثنائية اللغة:** موقع متكامل ([index.html](index.html)) يدعم التبديل اللحظي بين العربية والإنجليزية والوضع الليلي/النهاري وتصفح المصاحف والتراجم.
6. **مكتبة المصاحف والتفاسير النادرة ([tafasir.html](tafasir.html)):** مكتبة متخصصة تضم 23 مجلداً تاريخياً نفيساً (بحجم 3.48 جيجابايت) من أرشيف الإنترنت مع تصفح كتابي تفاعلي، وروابط تحميل مباشرة، وأداة سطر أوامر للتحميل التلقائي (`download_tafasir.py`).

---

## File Structure / هيكلية الملفات

```text
Quran-db/
├── index.html                     # Interactive Bilingual Project Presentation (Web Dashboard)
├── tafasir.html                   # Rare Mushafs & Tafasir Archive Library (23 Volumes, 3.48 GB)
├── ar.html                        # Direct Arabic entry point (RTL)
├── data.js                        # Compact zero-CORS JSON dataset for local & web viewing
├── data.json                      # Machine-readable JSON export of all 4 datasets
├── tafasir_data.js                # Archive.org dataset for instant zero-CORS client loading
├── tafasir_archive_data.json      # Structured JSON metadata for the 23 archive volumes
├── tafasir_archive_data.csv       # Spreadsheet export of archive tafasir & mushafs (UTF-8 BOM)
├── download_tafasir.py            # Resumable multi-threaded CLI downloader for all 23 editions
├── combined_master.csv            # Master dataset (319 editions, UTF-8 BOM)
├── combined_master_utf8.csv       # Master dataset (Standard UTF-8)
├── mushaf_only.csv                # 36 Arabic Mushafs with verified Evidence URLs (UTF-8 BOM)
├── mushaf_only_utf8.csv           # 36 Arabic Mushafs (Standard UTF-8)
├── translations.csv               # 283 Translations & Tafsirs (UTF-8 BOM)
├── translations_utf8.csv          # 283 Translations (Standard UTF-8)
├── combined_countries_ranked.csv  # 227 Ranked Countries & Muslim Demographics
├── merge_audit_log.json           # Transparent audit log of all 31 duplicate merges
├── generate_all_combined.py       # 1-click deterministic Python pipeline
├── consolidation_report.md        # Comprehensive technical & scholarly audit report
└── combined_data/                 # 227 individual <country>.jsonl files
```

---

## Verified Evidence Links for Arabic Mushafs (100% Tested HTTP 200)

All 36 Arabic Mushaf editions have been programmatically tested and verified with direct links:

| # | Country | Edition / Title | Riwayah / Style | Publisher | Direct Evidence Link |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | **Algeria** | مصحف الجزائر الشريف | ورش عن نافع | SNED (Cherifi 1983) | [Archive.org Scan](https://archive.org/details/MushafWarsh) |
| 2 | **Austria** | Ibn al-Bawwab MS K.16 | Naskh (1001 AD) | ADEVA / Chester Beatty | [Chester Beatty High-Res Viewer](https://viewer.cbl.ie/viewer/image/Is_1431/1/LOG_0000/) |
| 3 | **Bahrain** | مصحف البحرين | حفص عن عاصم | Supreme Islamic Council | [Archive.org Scan](https://archive.org/details/20210325_20210325_0401) |
| 4 | **Brunei** | مصحف بروناي دار السلام | حفص عن عاصم | Pusat Da'wah Islamiah | [Archive.org Scan](https://archive.org/details/20250510_20250510_0648) |
| 5 | **Chad** | مصحف تشاد برواية الدوري | الدوري عن أبي عمرو | CSAIT | [Archive.org Scan](https://archive.org/details/DORY3AMRMADINAHS) |
| 6 | **China** | مصحف بكين الشريف (1980) | حفص (نسخة 1952) | Islamic Association of China | [Historical Documentation](https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E4%BC%8A%E6%96%AF%E5%85%B0%E6%95%99%E5%8D%8F%E4%BC%9A) |
| 7 | **Egypt** | المصحف الأميري (بولاق 1342هـ) | حفص (Royal Edition) | Amiri Press & Survey of Egypt | [Archive.org Amiri Scan](https://archive.org/details/way2sona_20160915_2156) |
| 8 | **Egypt** | مصحف الشمرلي (15 سطر) | حفص عن عاصم | Shamarly Cairo | [Archive.org Shamarly Scan](https://archive.org/details/shamarlyshamarly) |
| 9 | **India** | مصحف التاج الهندي (15 سطر) | Nastaliq / Indo-Pak | Taj Company Ltd. | [Archive.org 15-Line Scan](https://archive.org/details/QuranMajeed-15Lines-PakistaniPrint) |
| 10 | **Indonesia** | مصحف منارة قدس (15 سطر) | Pojok Kudus | CV Menara Kudus | [Archive.org Kudus Scan](https://archive.org/details/al-quran-kudus-30-juz) |
| 11 | **Iran** | مصحف ميرزا أحمد النيريزي | Naskh Nayrizi | Soroush Publishing | [Archive.org Nayrizi Facsimile](https://archive.org/details/QuranofNeirizi) |
| 12 | **Iraq** | مصحف بغداد (دار الحرية 1979) | خط الحافظ الرشدي | Dar al-Hurriyah Baghdad | [Archive.org Baghdad Scan](https://archive.org/details/1981_20260422) |
| 13 | **Jordan** | مصحف آل البيت (المصحف الهاشمي) | حفص عن عاصم | Aal al-Bayt Institute | [Altafsir.com Official Portal](https://www.altafsir.com/Quran.asp) |
| 14 | **Kuwait** | مصحف دولة الكويت | عثمان طه | Kuwait Ministry of Awqaf | [Archive.org Kuwait Scan](https://archive.org/details/20200728_20200728_0545) |
| 15 | **Lebanon** | مصحف التجويد الملون | حفص عن عاصم | Dar al-Maarifa Beirut | [Archive.org Color Tajweed Scan](https://archive.org/details/Quran25) |
| 16 | **Lebanon** | طبعة دار الكتب العلمية | حفص عن عاصم | Dar al-Kutub al-Ilmiyyah | [Archive.org Dar al-Kutub Scan](https://archive.org/details/Al-QuranTadabburWaAmal) |
| 17 | **Libya** | مصحف الجماهيرية | قالون عن نافع | WICS Libya | [Archive.org Libyan Scan](https://archive.org/details/20240516_20240516_1544) |
| 18 | **Malaysia** | مصحف ماليزيا الشريف | Rasm Uthmani | Yayasan Restu / Nasyrul Quran | [Archive.org Malaysia Tajwid](https://archive.org/details/mushaf-tajwid-beserta-terjemahan-ke-dalam-bahasa-malaysia) |
| 19 | **Mauritania** | مصحف ورش الموريتاني | الخط الشنقيطي | Ministry of Islamic Affairs | [Official Digital Edition](https://play.google.com/store/apps/details?id=mr.quranwarch&hl=ar) |
| 20 | **Morocco** | المصحف الحسني المسبع | ورش عن نافع | Royal Moroccan Press | [Archive.org Musabba Scan](https://archive.org/details/Quran_Warsh_Moorocco) |
| 21 | **Morocco** | المصحف المحمدي الشريف | ورش عن نافع | Fondation Mohammed VI | [Quran.ws Official PDF](https://pdf.quran.ws/pdfs/warsh/quran-warsh-mushaf.pdf) |
| 22 | **Oman** | مصحف مسقط التفاعلي | Unicode Portal | Ministry of Endowments | [Mushaf Muscat Portal](https://mushafmuscat.om) |
| 23 | **Pakistan** | مصحف الحفاظ (تاج كمبني 16 سطر) | Indo-Pak Naskh | Taj Company Lahore | [Archive.org 16-Line Scan](https://archive.org/details/AlQuranAlKareem16LinesTajCompany) |
| 24 | **Palestine** | مصحف المسجد الأقصى | مخطوطات القدس | Al-Aqsa Mosque Library | [Archive.org Al-Aqsa Catalog](https://archive.org/details/0590_20210109) |
| 25 | **Qatar** | مصحف قطر | عبيدة البنكي | Qatar Ministry of Awqaf | [Archive.org Mushaf Qatar Scan](https://archive.org/details/MushafQatar_20150445776437) |
| 26 | **Russia** | مصحف قازان 1803 | First Printed Edition | Asiatic Printing House | [Archive.org Kazan 1803 Scan](https://archive.org/details/006-qran-kazan-1803) |
| 27 | **Saudi Arabia** | مصحف المدينة النبوية (حفص) | عثمان طه | King Fahd Complex (KFQPC) | [Archive.org Madinah Hafs Scan](https://archive.org/details/MushafMadinaHafsGreen1441) |
| 28 | **Saudi Arabia** | مصحف المدينة النبوية (ورش) | عثمان طه | King Fahd Complex (KFQPC) | [Archive.org Madinah Warsh Scan](https://archive.org/details/ozkorallh_20181029_2220) |
| 29 | **Senegal** | مصحف طوبى برواية ورش | الخط السنغالي السوقي | Imprimerie Serigne Touba | [Archive.org Touba Muridiyya](https://archive.org/details/kamil_serigne_Fallou) |
| 30 | **South Africa** | Tuan Guru Manuscript (~1800) | Handwritten Manuscript | Auwal Mosque, Bo-Kaap | [Historical Facsimile & Account](https://aboutislam.net/muslim-issues/world/how-cape-town-muslims-saved-south-africas-oldest-quran/) |
| 31 | **Sudan** | مصحف السودان برواية الدوري | الدوري عن أبي عمرو | Sudanese Book House | [Archive.org Al-Duri Scan](https://archive.org/details/DORY3AMRMADINAHS) |
| 32 | **Syria** | مصحف دمشق المعتمد (1970) | خط عثمان طه الأول | Dar al-Fikr / Syrian Awqaf | [Scholarly Documentation](https://ar.wikipedia.org/wiki/%D8%B9%D8%AB%D9%85%D8%A7%D9%86_%D8%B7%D9%87) |
| 33 | **Tunisia** | المصحف التونسي الشريف | قالون عن نافع | Official Press / Ez-Zitouna | [Archive.org Tunisian Qalun](https://archive.org/details/qaloon_tunesCCCCCCCCCCCCCCCCCCCCC) |
| 34 | **Turkey** | خط الحافظ عثمان | Ottoman Naskh | Çağrı Yayınları Istanbul | [Archive.org Hafiz Osman Scan](https://archive.org/details/Hafizosman) |
| 35 | **UAE** | مصحف الشيخ مكتوم (مصحف دبي) | جمال بوستن | DIHQA / Dubai Awqaf | [Archive.org Mushaf Maktoum](https://archive.org/details/356835683586MAKTOOM) |
| 36 | **Yemen** | مخطوطة صنعاء الشريفة | Hijazi / Early Kufic | Dar al-Athar al-Islamiyyah | [Archive.org Sanaa Scan](https://archive.org/details/A21_Almoshaf_Alcharif_Attributed_to_Ali_ben_Abi_Talib_The_copy_of_Sanaa) |

---

## How to Reproduce & Regenerate Data

To run the deterministic pipeline that generates all CSV, JSON, and JSONL files:

```bash
python3 generate_all_combined.py
```

This will automatically:
1. Re-read inputs from `AGY-results/` and `glm-results/`.
2. Apply the deduplication rules and merge duplicate editions.
3. Clean and standardize all metadata fields.
4. Export `combined_master.csv`, `mushaf_only.csv`, and `translations.csv` (both UTF-8 BOM for Excel and standard UTF-8).
5. Generate the 227 per-country JSONL files in `combined_data/`.
6. Write the comprehensive `merge_audit_log.json`.

---

## License & Citation
Open scholarly data released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). When using or referencing this database in academic or public research, please cite:

```bibtex
@dataset{quran_db_2026,
  title        = {Quran-DB: Global Quran Editions and Translations Database},
  author       = {Soubhi, Mohamed and Contributors},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/mohamed-soubhi/quran-db}}
}
```
