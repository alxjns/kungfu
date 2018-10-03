#!/usr/bin/python

import yaml
import re

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

def generateKarate(yamlFile):
    docs = yaml.load(yamlFile)
    try:
        properties = docs['properties']
    except:
        print("No properties found in file")
        return
    return processProperties(properties)
