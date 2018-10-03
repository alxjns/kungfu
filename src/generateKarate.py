#!/usr/bin/python

import yaml
import json

def getKarateType(prop):
    oasType = prop.get('type', 'other')
    karateType = '#notnull'

    if oasType in ('string', 'number', 'boolean', 'array', 'object'):
        karateType = '#' + oasType
    elif oasType == 'integer':
        karateType = '#number'

    nullable = prop.get('nullable', False)
    if nullable:
        karateType = '#' + karateType

    return karateType

def generateKarate(yamlFile):
    docs = yaml.load(yamlFile)
    try:
        properties = docs['properties']
    except:
        print("No properties found in file")
        return
    karate = {}
    for prop in properties.keys():
        # WriteOnly properties are not part of the response
        writeOnly = properties[prop].get('writeOnly', False)
        if writeOnly:
            continue 

        karate[prop] = getKarateType(properties[prop])

    karateJson = json.dumps(karate, indent=4) 
    print(karate)
