from functools import partial
import os
import re
import textwrap


class RefResolver:
    def resolve_ref_callback(self, match, base_filename):
        filename = os.path.abspath(os.path.join(os.path.dirname(base_filename), match.group(2)))
        spacing_block = match.group(1)
        spacing_length = len(spacing_block)
        spacing = " " * spacing_length
        return textwrap.indent(self.resolve(filename), spacing)

    def replace_refs(self, file_obj):
        # Find any $ref instances and replace them with their file content via callback
        return re.sub(r'([ -]+)\$ref: \'(.*)\'$', partial(self.resolve_ref_callback, base_filename=file_obj.name), file_obj.read(), flags=re.MULTILINE)

    """Initializes the recursive resolution of $ref files"""
    def resolve(self, filename):
        with open(filename, 'r') as f:
            return self.replace_refs(f)
