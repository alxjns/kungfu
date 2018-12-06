#!/usr/bin/python

import os
import json
from argparse import ArgumentParser
from generateKarate import generateKarateFromYaml, generateKarateFromJson

parser = ArgumentParser('Process a compiled spec file into Karate JSON')
parser.add_argument('input', help='Path of file or folder for processing')
parser.add_argument('-o', '--out', default='kungfu-output', help='Folder where output will be written')
args = parser.parse_args()

file_or_directory_path = args.input
outFolderName = args.out

try:
    os.mkdir(outFolderName)
except FileExistsError:
    pass

def create_karate_json_of_yaml(yamlFilePath):
    with open(yamlFilePath, 'rb') as f:
        print("Reading " + yamlFilePath)
        karate = generateKarateFromYaml(f)
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

def parse_full_json_spec(inputFilePath):
    print("Processing JSON file")
    with open(inputFilePath, 'rb') as f:
        print("Reading " + inputFilePath)
        karateSchemas = generateKarateFromJson(f)
    if karateSchemas is None:
        print("Not writing output")
        return

    for schema in karateSchemas:
        matcher = karateSchemas[schema]
        if (matcher is None) or ('Kungfu error' in matcher):
            print("A valid matcher was NOT created for", schema)
        outFileName = schema + '.json'
        outFilePath = os.path.join(outFolderName, outFileName)
        with open(outFilePath, 'w') as fp:
            json.dump(matcher, fp, indent=4)
            print("Wrote to: " + outFilePath)
            #print(json.dumps(karateSchemas[schema], indent=4))
        
if os.path.isfile(file_or_directory_path):
    if os.path.splitext(file_or_directory_path)[1] == '.json':
                parse_full_json_spec(file_or_directory_path)
    else:
        create_karate_json_of_yaml(file_or_directory_path)

if os.path.isdir(file_or_directory_path):
    for path in os.listdir(file_or_directory_path):
        fullpath = os.path.join(file_or_directory_path, path)
        if os.path.isfile(fullpath):
            if os.path.splitext(fullpath)[1] == '.json':
                parse_full_json_spec(fullpath)
            else:
                create_karate_json_of_yaml(fullpath)
