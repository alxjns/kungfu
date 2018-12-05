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
            #print(pp.pprint(schemas[schema]['properties']))
            karate_schemas[schema] = processProperties(properties)
            print('Got properties')
        except:
            try:
                properties = schemas[schema]['allOf']
                #print(pp.pprint(schemas[schema]['allOf']['properties']))
                #karate_schemas[schema] = processProperties(properties)
                print('Got allOf found in schema')
                continue
            except:
                try:
                    properties = schemas[schema]['description']
                    print('Got description found in schema')
                    continue
                except:
                    print(pp.pprint(schemas[schema]))
                    print(schemas[schema].keys())
                    print('No properties or allOf found in schema')

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
