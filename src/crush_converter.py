class Formatter(object):
    def __init__(self):
        pass

    def get_content(self):
        pass

    def format_section(self, items):
        pass

    def format_item(self, typename, name, props): 
        pass


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
        self._formatter.format_oneline_section('type',
                ['osd', 'node', 'zone', 'storage_group', 'root'])

    def add_devices(self):
        self._formatter.format_oneline_section('device',
                map(lambda item: item['name'], self._osdtree.get_osds()))

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
