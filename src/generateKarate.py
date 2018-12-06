#!/usr/bin/python

import yaml
import json
import re
import pprint
from refRetriever import RefRetriever

pp = pprint.PrettyPrinter(depth=3)

def getEnumMatcher(enumYaml):
    matcher = "#regex("
    for value in enumYaml:
        escaped = re.sub(r"-", r"\\-", value)
        matcher += (escaped + "|")
    matcher = matcher[:-1] + ")"
    return matcher

def processRefProperty(prop):
    """
    Given an OpenApi property object with a $ref, returns the content the $ref points to.
    Except, if the $ref is in the blacklist `links_not_to_follow`, returns the original property. 
    """
    
    links_not_to_follow = ["#/components/schemas/Links"]
    if prop['$ref'] in links_not_to_follow:
        return prop
    
    refhelper = RefRetriever(prop['$ref'], docs)
    return refhelper.refTarget
    

def getKarateType(prop):
    """
    Given an OpenApi property object, returns a Karate fuzzy matcher
    """
    karateType = '#notnull'

    if (not 'type' in prop) and ('$ref' in prop) and docs:
        prop = processRefProperty(prop)
        
    oasType = prop.get('type', None)

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

def processAllOfInSchema(items):
    """
    This should take the contents of a AllOf and return some valid Karate matcher
    TODO: make this work
    """
    return {'Kungfu error': 'schema type: allOf'}

def processOneOfInSchema(items):
    """
    This should take the contents of a OneOf and return some valid Karate matcher
    TODO: make this work
    """
    return {'Kungfu error': 'schema type: oneOf'}

def processSchema(schema):
    """
    This takes a schema object and returns its best guess of a Karate matcher for the schema
    """
    if 'properties' in schema:
        return processProperties(schema['properties'])
    elif 'allOf' in schema:
        return processAllOfInSchema(schema['allOf'])
    elif 'oneOf' in schema:
        return processOneOfInSchema(schema['oneOf'])
    else:
        print('No properties found in schema')
        pp.pprint(schema)
        return None

def processSchemas(schemas):
    """
    This takes an object comprised of schemas and returns an object with a Karate matcher for each schema
    """
    #pp.pprint(schemas)
    karate_schemas = {}
    for schema in schemas:
        karate_schemas[schema] = processSchema(schemas[schema])
    return karate_schemas

def generateKarateFromYaml(yamlFile):
    schema = yaml.load(yamlFile)
    return processSchema(schema)

def generateKarateFromJson(inputFile):
    global docs
    docs = json.load(inputFile)
    try:
        schemas = docs['components']['schemas']
        print("got schemas")
    except:
        print("No schemas found in file")
        return
    return processSchemas(schemas)
