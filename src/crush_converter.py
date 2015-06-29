import json
import itertools

class Formatter(object):
    def __init__(self):
        self.lines = []

    def get_content(self):
        return '\n'.join(self.lines)

    def _add_section_sep(self):
        self.lines.append(str())

    def _format_oneline_section(self, typename, items, num=0):
        self.lines.append('# %ss' % typename)
        for i, item in enumerate(items, start=num):
            self.lines.append("%s %d %s" % (typename, i, item))
        self._add_section_sep()
        return len(items) + num

    def format_devices(self, items):
        return self._format_oneline_section('device', items)

    def format_types(self, items):
        return self._format_oneline_section('type', items)

    def format_multiline_section(self, typename, name, *props):
        self.lines.append('%s %s {' % (typename, name))
        for prop in props:
            self.lines.append('    %s' % (' '.join(prop)))
        self.lines.append('}')


class OSDTree(object):
    def __init__(self, osdtreemap):
        self._osdtreemap = osdtreemap
        self._items = osdtreemap['nodes']

    def _get_items_by_type(self, typename):
        return filter(lambda item: typename == item['type'], self._items)

    def get_osds(self):
        return self._get_items_by_type('osd')

    def get_hosts(self):
        return self._get_items_by_type('host')


class LLC(object):
    def __init__(osdtree, formatter):
        self._formatter = formatter
        self._osdtree = osdtree

    def _get_hostosd_list(self):
        pass

    def validate_map(self):
        return True

    def add_types(self):
        self._formatter.format_types(
                ['osd', 'node', 'zone', 'storage_group', 'root'])

    def add_devices(self):
        self._formatter.format_devices(self._osdtree.get_osds_names())

    def add_hosts_osds(self):
        hosts = self._osdtree.get_hosts()
        names = map(lambda item: item['name'], hosts)

        for entity in itertools.product(names, self._storage_groups,
                self._zones):
            entity_name = '_'.join(entity)
            properties = {}
            properties['id'] = '-1'
            properties['alg'] = 'straw'
            properties['hash'] = '0'
            properties['item'] = []
            self._formatter.format_multiline_section('host', entity_name,
                    properties)

    def add_root(self):
        pass

    def add_storage_groups(self):
        for storage_group in self._storage_groups:
            self._formatter.format_multiline_section('storage_group',
                    storage_group, {})

    def add_zones(self):
        for entity in itertools.product(self._zones, self._storage_groups):
            entity_name = '_'.join(entity)
            self._formatter.format_multiline_section('zone', entity_name, {})

    def add_rulesets(self):
        pass

if __name__ == '__main__':
    with open('/tmp/hier.txt', 'r') as fh:
        osdtree = OSDTree(json.loads(fh.read()))
        formatter = Formatter()

        conv = Converter(osdtree, formatter)
        conv.add_types()
        conv.add_devices()
        conv.add_hosts_osds()
        conv.add_zones()
        conv.add_storage_groups()
        print(formatter.get_content())
    pass
