#!/usr/bin/python

import os
import json
from argparse import ArgumentParser
from generateKarate import generateKarate

parser = ArgumentParser('Process spec files into Karate JSON')
parser.add_argument('input', help='Path of file or folder for processing')
parser.add_argument('-o', '--out', default='kungfu-output', help='Folder where output will be written')
args = parser.parse_args()

file_or_directory_path = args.input
outFolderName = args.out

try:
    os.mkdir(outFolderName)
except FileExistsError:
    pass

def create_karate_json_of_file(yamlFilePath):
    with open(yamlFilePath, 'rb') as f:
        print("Reading " + yamlFilePath)
        karate = generateKarate(f)
    if karate is None:
        print("Not writing output")
        return

    inFileName = os.path.basename(yamlFilePath)
    outFileName = os.path.splitext(inFileName)[0] + '.json'
    outFilePath = os.path.join(outFolderName, outFileName)
    with open(outFilePath, 'w') as fp:
        json.dump(karate, fp, indent=4)
        print("Wrote to: " + outFilePath)
        #print(json.dumps(karate, indent=4))
        
if os.path.isfile(file_or_directory_path):
    create_karate_json_of_file(file_or_directory_path)

if os.path.isdir(file_or_directory_path):
    for path in os.listdir(file_or_directory_path):
        fullpath = os.path.join(file_or_directory_path, path)
        if os.path.isfile(fullpath):
            create_karate_json_of_file(fullpath)
