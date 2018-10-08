#!/usr/bin/python

from argparse import ArgumentParser
import json
import os

from karate import generate_karate
from ref_parser import RefResolver

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


def create_karate_json_of_file(yaml_file_path):
    with open(yaml_file_path, 'rb') as f:
        print("Reading " + yaml_file_path)
        ref_resolver = RefResolver()
        yaml_content = ref_resolver.resolve(yaml_file_path)
        print(yaml_content)
        karate = generate_karate(yaml_content)
    if karate is None:
        print("Not writing output")
        return

    in_filename = os.path.basename(yaml_file_path)
    out_filename = os.path.splitext(in_filename)[0] + '.json'
    out_file_path = os.path.join(outFolderName, out_filename)
    with open(out_file_path, 'w') as fp:
        json.dump(karate, fp, indent=4)
        print("Wrote to: " + out_file_path)
        #print(json.dumps(karate, indent=4))


if __name__ == "__main__":
    if os.path.isfile(file_or_directory_path):
        create_karate_json_of_file(file_or_directory_path)

    if os.path.isdir(file_or_directory_path):
        for path in os.listdir(file_or_directory_path):
            fullpath = os.path.join(file_or_directory_path, path)
            if os.path.isfile(fullpath):
                create_karate_json_of_file(fullpath)
