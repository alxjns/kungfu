#!/usr/bin/python

import os.path as os_path
import re

import yaml

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

def processProperties(properties, rootFilePath = None):
    karate = {}
    for prop in properties.keys():
        # WriteOnly properties are not part of the response
        writeOnly = properties[prop].get('writeOnly', False)
        if writeOnly:
            continue

        refFilePath = properties[prop].get('$ref')

        if refFilePath:
            rootFileDir = os_path.dirname(rootFilePath)
            absRefFilePath = os_path.abspath(os_path.join(rootFileDir, refFilePath))

            if os_path.isfile(absRefFilePath):
                with open(absRefFilePath, 'r') as fp:
                    refDoc = yaml.load(fp)
                    if 'oneOf' in refDoc:
                        karateTypes = []
                        for element in refDoc['oneOf']:
                            karateTypes.append(getKarateType(element))

                        karate[prop] = '|'.join(karateTypes)
                    else:
                        karate[prop] = getKarateType(refDoc)
        else:
            karate[prop] = getKarateType(properties[prop])

    return karate

def generateKarate(yamlFile):
    docs = yaml.load(yamlFile)
    try:
        properties = docs['properties']
    except:
        print("No properties found in file")
        return
    return processProperties(properties, yamlFile.name)
