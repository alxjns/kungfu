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


def processRefProperty(prop):
    """
    Given an OpenApi property object with a $ref,
    returns the content the $ref points to.
    Except, if the $ref is in the blacklist `links_not_to_follow`,
    returns the original property.
    """
    from refRetriever import RefRetriever
    links_not_to_follow = ["#/components/schemas/Links"]
    if prop['$ref'] in links_not_to_follow:
        return {}

    refhelper = RefRetriever(prop['$ref'], docs)
    return refhelper.refTarget


def getKarateType(prop):
    """
    Given an OpenApi property object, returns a Karate fuzzy matcher
    """
    karateType = '#notnull'

    if ('type' not in prop) and ('$ref' in prop) and docs:
        # Use the $ref and ignore the rest of the contents of this property
        prop = processRefProperty(prop)
        ref_as_schema = processSchema(prop)
        if ref_as_schema:
            return ref_as_schema
        return getKarateType(prop)

    openApiType = prop.get('type')

    if openApiType in ('string', 'number', 'boolean', 'array', 'object'):
        karateType = '#' + openApiType
    elif openApiType == 'integer':
        karateType = '#number'

    enum = prop.get('enum')
    if openApiType == 'string' and enum:

        karateType = getEnumMatcher(enum)

    nullable = prop.get('nullable')
    if nullable:
        karateType = '#' + karateType

    # Process details of non-nullable objects.
    # (We can't validate nullable objects in the same file.)
    if karateType == '#object': 
        childProperties = prop.get('properties')
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

        allOf = properties[prop].get('allOf')
        if allOf:
            karate[prop] = processAllOfInProperty(allOf)
        else:
            karate[prop] = getKarateType(properties[prop])

    return karate

def processAllOfInProperty(items):
    """
    This should take the contents of a AllOf in a Property
    and return some valid Karate matcher

    * Could be two types
    * Could be a type and a "nullable"
    * Etc.
    """
    karateType = '#notnull'
    nullable = False
    types = []
    for item in items:
        item_type = getKarateType(item)
        if not item_type == karateType:
            types.append(item_type)
        item_is_nullable = item.get('nullable')
        if item_is_nullable:
            nullable = True

    if len(types) == 1:
        karateType = types[0]
    if nullable:
        if karateType[0] == "{":
            # Nullable objects MUST be represented as ##object
            karateType = '##object'
        elif not karateType[0:2] == '##':
            # Mark nullable properties as optional in Karate
            karateType = '#' + karateType

    return karateType

def processAllOfInSchema(items):
    """
    This should take the contents of a AllOf
    and return some valid Karate matcher
    """
    karate = {}
    for item in items:
        item_karate = processSchema(item)
        if(item_karate):
            karate = {**karate, **item_karate}
    return karate


def merge_schemas(target_schema, adding_schema):
    """
    This takes two schemas and combines them into one
    """
    for key in adding_schema.keys:
        if target_schema.get(key):
            pass
        else:
            target_schema[key] = adding_schema[key]
    return target_schema


def processSchema(schema):
    """
    This takes a schema object and returns its best guess of a Karate matcher for the schema
    """

    if 'properties' in schema:
        return processProperties(schema['properties'])
    elif 'allOf' in schema:
        return processAllOfInSchema(schema['allOf'])
    elif '$ref' in schema:
        ref_schema = processRefProperty(schema)
        return processSchema(ref_schema)
    else:
        # No properties found in schema
        return None

def processSchemas(schemas):
    """
    This takes an object comprised of schemas and returns an object with a Karate matcher for each schema
    """

    karate_schemas = {}
    for schema in schemas:
        if 'oneOf' in schemas[schema]:
            for sub_schema in schemas[schema]['oneOf']:
                title = schema + '-' + sub_schema['title']
                karate_schemas[title] = processSchema(sub_schema)
            continue
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
