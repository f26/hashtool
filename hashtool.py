#!/usr/bin/python3

# A hash tool to generate and compare hash files for a directory.  The hash file contains the last
# modified date, the hash, and the path of each file in the directory.  The tool can be used to
# detect changes in the files in the directory by comparing the current hash file with a previously
# generated one.  If changes are detected, the user can choose to replace the old hash file with
# the new one.

import os
import hashlib
import datetime
import time as time_module
import sys
import shutil
from pathlib import Path

HASH_FILE = ".hashes.txt"
HASH_FILE_TMP = ".hashes.txt.tmp"

def main():
    # If temp file exists, last run was interrupted, remove it and start fresh
    if os.path.exists(HASH_FILE_TMP):
        print(f"WARN: Found temporary hash file {HASH_FILE_TMP}, removed it")
        os.remove(HASH_FILE_TMP)

    # If no hash file exists, there's nothing to compare, just create one
    if not os.path.exists(HASH_FILE):
        create_hash_file(HASH_FILE)
        print("Hash file created")
        return

    # If execution gets here, a hash file exists, regenerate and compare
    create_hash_file(HASH_FILE_TMP)
    result = os.system(f"diff -u0 {HASH_FILE} {HASH_FILE_TMP}")
    if(result == 0):
        print("No changes detected")
        return # Nothing to do, so bail out here
    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!! Changes detected !!!!!!!!!!!!!!!!!!!!!!!!!!")
    os.system(f"diff -u0 {HASH_FILE} {HASH_FILE_TMP} | colordiff")

    # At this point we know the hash files differ.  Ask the user if they want to replace the
    # old hash file with the new one
    while True:
        answer = input("Replace old hash file with new one? (type 'yes', anything else is no): ")
        if answer.lower() == 'yes':
            shutil.move(HASH_FILE_TMP, HASH_FILE)
            print(f"Hash file verification complete, hash file updated")
            return
        os.remove(HASH_FILE_TMP)
        print(f"Hash file verification complete, no changes applied")
        return;

def md5(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(1024*1024):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def create_hash_file(hash_file: str):
    # Compile a list of files, skipping the hash file and temp hash file, then sort it
    file_list = []
    for root, dirs, files in os.walk('./'):
        for file in files:

            if(file.endswith(HASH_FILE) or file.endswith(HASH_FILE_TMP)):
                continue
            file_list.append(os.path.join(root, file)) 
    file_list.sort()

    # Save the hash file and print to screen
    with open(hash_file, "w", encoding="utf-8") as f:
        for path in file_list:
            hash = md5(path)
            dt = str(datetime.datetime.fromtimestamp(os.path.getmtime(path)))
            if len(dt) == 19: # If there is no decimal component, pad with zeros
               dt = f"{dt}.000000"

            # Get rid of non-utf8 encodable chars
            path = str(path.encode('utf-8', 'ignore'))
            path = path[2:]
            path = path[:-1]

            print(f"{dt} {hash} {path}")
            f.write(f"{dt} {hash} {path}\n")

if __name__ == "__main__":
    main()
