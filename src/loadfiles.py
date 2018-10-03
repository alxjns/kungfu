#!/usr/bin/python

import os
from generateKarate import generateKarate

file_or_directory_path = '/Users/user/schemas/'

def do_something(fileobj):
    generateKarate(fileobj)

if os.path.isfile(file_or_directory_path):
    with open(file_or_directory_path, 'rb') as f:
        print(file_or_directory_path)
        do_something(f)

if os.path.isdir(file_or_directory_path):
    for path in os.listdir(file_or_directory_path):
        fullpath = os.path.join(file_or_directory_path, path)
        if os.path.isfile(fullpath):
            with open(fullpath, 'rb') as f:
                print(fullpath)
                do_something(f)
