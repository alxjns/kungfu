#!/usr/bin/python

import re

import yaml


def get_enum_matcher(enumYaml):
    matcher = "#regex("
    for value in enumYaml:
        escaped = re.sub(r"-", r"\\-", value)
        matcher += (escaped + "|")
    matcher = matcher[:-1] + ")"
    return matcher


def get_karate_type(prop):
    oas_type = prop.get('type', None)
    karate_type = '#notnull'

    if oas_type in ('string', 'number', 'boolean', 'array', 'object'):
        karate_type = '#' + oas_type
    elif oas_type == 'integer':
        karate_type = '#number'

    enum = prop.get('enum', None)
    if oas_type == 'string' and enum is not None:
        karate_type = get_enum_matcher(enum)

    nullable = prop.get('nullable', False)
    if nullable:
        karate_type = '#' + karate_type

    if oas_type == 'object':
        child_properties = prop.get('properties', False)
        if child_properties:
            karate_type = process_properties(child_properties)

    return karate_type


def process_properties(properties):
    karate = {}
    for prop in properties.keys():
        # WriteOnly properties are not part of the response
        write_only = properties[prop].get('writeOnly', False)
        if write_only:
            continue

        if 'oneOf' in properties[prop]:
            karate_types = []
            for element in properties[prop].get('oneOf'):
                karate_types.append(get_karate_type(element))

            karate[prop] = '|'.join(karate_types)
        else:
            karate[prop] = get_karate_type(properties[prop])

    return karate


def generate_karate(yaml_doc):
    docs = yaml.load(yaml_doc)
    try:
        properties = docs['properties']
    except KeyError:
        print("No properties found in document")
        return
    return process_properties(properties)
