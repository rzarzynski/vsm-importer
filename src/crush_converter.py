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
        pass

    def add_root(self):
        pass

    def add_storage_groups(self):
        pass

    def add_zones(self):
        pass

    def add_rulesets(self):
        pass

if __name__ == '__main__':
    pass
