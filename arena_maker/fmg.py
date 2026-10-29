"""Editing text (FMG) as WitchyBND XML: <fmg> ... <entries><text id="...">text</text></entries>."""
from xml.etree import ElementTree


class FmgXml:
    def __init__(self, path: str):
        self.path = path
        self.tree = ElementTree.parse(path)
        self.entries = self.tree.getroot().find("entries")

    def set_text(self, text_id: int, text: str):
        """Replaces the entry with this ID, or inserts a new one in ID order."""
        for entry in self.entries:
            if int(entry.get("id")) == text_id:
                entry.text = text
                return
        entry = ElementTree.Element("text", {"id": str(text_id)})
        entry.text = text
        index = next((i for i, e in enumerate(self.entries) if int(e.get("id")) > text_id), len(self.entries))
        self.entries.insert(index, entry)

    def save(self):
        self.tree.write(self.path, encoding="utf-8", xml_declaration=True)
