#!/usr/bin/python

from copy import deepcopy

class RefRetriever():
    def __init__(self: object, refString: str, specFile: dict):
        """
        When an object is instantiated, it immediately processes the reference
        and saves the result to instance variable `refTarget`.
        """
        self.refString = refString
        self.specFile = specFile
        self.refTarget = self.getJsonForRef()

    def convertRefStringToKeyList(self):
        """
        This creates a list of the keys/indices needed to exctract the desired JSON from the specification object.
        It removes leading # and converts strings to integers where possible.
        """
        pathList = self.refString.split('/')
        pathList.remove('#')
        for i in range(len(pathList)):
            try:
                pathList[i] = int(pathList[i])
            except ValueError:
                pass
        return pathList

    def getJsonForRef(self):
        """
        Returns the part of the spec that the $ref refers to.
        """
        pathList = self.convertRefStringToKeyList()
        jsonSnip = deepcopy(self.specFile)

        for key in pathList:
            jsonSnip = jsonSnip[key]
        return jsonSnip

# You can run this file alone if you set `ref` and `inputFilePath` below
if __name__ == "__main__":
    import json
    ref = '#/components/schemas/SomeReferencedSchema'
    inputFilePath = '/test/this/file.json'
    with open(inputFilePath, 'rb') as f:
        docs = json.load(f)
        print("Reading " + inputFilePath)

        openapiref = RefRetriever(ref, docs)
        jsonRef = openapiref.refTarget
        print("result:", jsonRef)
