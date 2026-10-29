"""Editing params as WitchyBND XML: <param> ... <rows><row id="..." field="value" .../></rows>.

Rows leave out fields that equal the field's defaultValue (see <fields>), so a cloned row keeps those defaults.
Field names are the current Paramdex ones (docs/arena_format.md).
"""
import copy
import os
from xml.etree import ElementTree


class ParamXml:
    def __init__(self, path: str):
        self.path = path
        self.tree = ElementTree.parse(path)
        self.rows = self.tree.getroot().find("rows")
        self.defaults = {f.get("name"): f.get("defaultValue") for f in self.tree.getroot().find("fields")}

    def values(self, row: ElementTree.Element) -> dict:
        """All of a row's fields, including the ones left out because they equal the default."""
        return {**self.defaults, **row.attrib}

    def row(self, row_id: int) -> ElementTree.Element:
        for row in self.rows:
            if row.get("id") == str(row_id):
                return row
        raise KeyError(f"Row {row_id} not found in {self.path}")

    def clone_row(self, source_id: int, new_id: int, **fields) -> ElementTree.Element:
        """Copies a row under a new ID (inserted in ID order) and sets the given fields."""
        if any(row.get("id") == str(new_id) for row in self.rows):  # E.g. a base mod already uses it
            raise ValueError(f"{os.path.basename(self.path)}: row {new_id} already exists")
        new_row = copy.deepcopy(self.row(source_id))
        new_row.set("id", str(new_id))
        for name, value in fields.items():
            new_row.set(name, str(value))
        index = next((i for i, row in enumerate(self.rows) if int(row.get("id")) > new_id), len(self.rows))
        self.rows.insert(index, new_row)
        return new_row

    def remove_row(self, row_id: int):
        self.rows.remove(self.row(row_id))

    def save(self):
        self.tree.write(self.path, encoding="utf-8", xml_declaration=True)
