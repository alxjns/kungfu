#!/usr/bin/python

import yaml
import json
import re
import pprint

pp = pprint.PrettyPrinter(depth=3)

def getEnumMatcher(enumYaml):
    matcher = "#regex("
    for value in enumYaml:
        escaped = re.sub(r"-", r"\\-", value)
        matcher += (escaped + "|")
    matcher = matcher[:-1] + ")"
    return matcher

def getKarateType(prop):
    oasType = prop.get('type', None)
    karateType = '#notnull'

    if oasType in ('string', 'number', 'boolean', 'array', 'object'):
        karateType = '#' + oasType
    elif oasType == 'integer':
        karateType = '#number'

    enum = prop.get('enum', None)
    if oasType == 'string' and enum is not None:
        karateType = getEnumMatcher(enum)

    nullable = prop.get('nullable', False)
    if nullable:
        karateType = '#' + karateType

    if oasType == 'object':
        childProperties = prop.get('properties', False)
        if childProperties:
            karateType = processProperties(childProperties)

    return karateType

def processProperties(properties):
    karate = {}
    for prop in properties.keys():
        # WriteOnly properties are not part of the response
        writeOnly = properties[prop].get('writeOnly', False)
        if writeOnly:
            continue 

        karate[prop] = getKarateType(properties[prop])
    
    return karate

def processSchemas(schemas):
    #pp.pprint(schemas)
    karate_schemas = {}
    for schema in schemas:
        print(schema)
        try:
            properties = schemas[schema]['properties']
            print('Got properties')
        except:
            print('No properties found in schema')
            continue
        karate_schemas[schema] = processProperties(properties)
    return karate_schemas

def generateKarateFromYaml(yamlFile):
    docs = yaml.load(yamlFile)
    try:
        properties = docs['properties']
    except:
        print("No properties found in file")
        return
    return processProperties(properties)

def generateKarateFromJson(inputFile):
    docs = json.load(inputFile)
    try:
        schemas = docs['components']['schemas']
        print("got schemas")
    except:
        print("No schemas found in file")
        return
    return processSchemas(schemas)
