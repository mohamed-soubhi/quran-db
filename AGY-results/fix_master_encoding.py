import os, time, shutil

src = 'master_utf8.csv'
dst = 'master.csv'

print(f"Waiting to update {dst} from {src} as soon as Excel closes it...")
updated = False
for attempt in range(60):
    try:
        shutil.copyfile(src, dst)
        print(f"SUCCESS: {dst} has been updated with UTF-8 BOM (utf-8-sig)!")
        updated = True
        break
    except PermissionError:
        time.sleep(1)

if not updated:
    print(f"File {dst} is still locked. Please close it in Microsoft Excel and re-run this script.")
