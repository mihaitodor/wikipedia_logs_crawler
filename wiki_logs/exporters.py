import json
from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes
from scrapy.utils.serialize import ScrapyJSONEncoder

class UnicodeJsonItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs)
        self.file = file
        kwargs.setdefault('ensure_ascii', not self.encoding)
        kwargs.setdefault('indent', 4)
        self.encoder = ScrapyJSONEncoder(**kwargs)
        self.first_item = True

    def start_exporting(self):
        self.file.write(b"[\n")

    def finish_exporting(self):
        self.file.write(b"\n]")

    def export_item(self, item):
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(b',\n')
        itemdict = dict(self._get_serialized_fields(item))
        data = self.encoder.encode(itemdict)
        self.file.write(to_bytes(data, self.encoding))
