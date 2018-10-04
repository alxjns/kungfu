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
    
        writeOnly = properties[prop].get('writeOnly', False)
        if writeOnly:
            continue # WriteOnly properties are not part of the response

        karate[prop] = getKarateType(properties[prop])
    
    return karate

def generateKarate(yamlFile):
    docs = yaml.load(yamlFile)
    
    properties = docs.get('properties', False)
    if properties:
        return processProperties(properties)

    allOf = docs.get('allOf', False)
    if allOf:
        for subschema in allOf:
            properties = subschema.get('properties', False)
            if properties:
                return processProperties(properties)

    print("No properties found in file")
    return
    
