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

    def format_bucket(self, typename, name, num, items):
        props = [
            ['id', str(num)],                                           \
            ['alg', 'straw'],                                           \
            ['hash', '0']                                               \
        ]
        for item, weight in items:
            props.append(['item', item, 'weight', str(weight)])
        self.format_multiline_section(typename, name, *props)


class OSDTree(object):
    def __init__(self, osdtreemap):
        self._osdtreemap = osdtreemap
        self._items = osdtreemap['nodes']

    def _get_items_by_type(self, typename):
        return filter(lambda item: typename == item['type'], self._items)

    def _get_item_by_name(self, itemname):
        return filter(lambda item: itemname == item['name'], self._items)[0]

    def _get_item_by_id(self, itemid):
        return filter(lambda item: itemid == item['id'], self._items)[0]

    def _get_osds(self):
        return self._get_items_by_type('osd')

    def _get_hosts(self):
        return self._get_items_by_type('host')

    def get_osd_names_by_host(self, hostname):
        try:
            oids = self._get_item_by_name(hostname)['children']
        except:
            return []
        else:
            return map(lambda oid: self._get_item_by_id(oid)['name'], oids)

    def get_osd_weights_by_host(self, hostname):
        try:
            oids = self._get_item_by_name(hostname)['children']
        except:
            return []
        else:
            return map(lambda oid: self._get_item_by_id(oid)['crush_weight'], oids)

    def get_osds_names(self):
        return map(lambda item: item['name'], self._get_osds())

    def get_hosts_names(self):
        return map(lambda item: item['name'], self._get_hosts())


class Converter(object):
    def __init__(self, osdtree, formatter):
        self._formatter = formatter
        self._osdtree = osdtree
        self._zones = ['zone0']
        # FIXME: convert to input params
        self._storage_groups = ['performance', 'capacity']
        self._mapping = {
            'capacity' : {
                    'zone0' : {
                        'rzarzynski-pc' : True
                    }
                }
            }
        self._bucket_num = 0
        self._ruleset_num = 0

    def _get_bucket_num(self):
        self._bucket_num = self._bucket_num - 1
        return self._bucket_num

    def _is_mapped(self, storage_group, zone, host):
        try:
            mapped = self._mapping[storage_group][zone][host]
        except KeyError:
            return False
        else:
            return mapped

    def _get_tree_weight(self, storage_group=None, zone=None, host=None):
        hosts  = [host] if host else self._osdtree.get_hosts_names()
        zones  = [zone] if zone else self._zones
        groups = [storage_group] if storage_group else self._storage_groups

        weight = 0
        for g, z, h in itertools.product(groups, zones, hosts):
            if self._is_mapped(g, z, h):
                weight = weight + sum(self._osdtree.get_osd_weights_by_host(h))
        return weight

    def _get_ruleset_item(self, group_name, ruleset_num=0):
        items = []
        items.append(['ruleset', str(self._ruleset_num)])
        items.append(['type', 'replicated'])
        items.append(['min_size', '0'])
        items.append(['max_size', '10'])
        items.append(['step', 'take', group_name])
        items.append(['step', 'chooseleaf', 'firstn', '0', 'type', 'host'])
        items.append(['step', 'emit'])
        self._ruleset_num = self._ruleset_num + 1
        return items

    def _get_root_items(self):
        return rootitems

    def _get_entity_name(self, *args):
        return '_'.join(args)

    def validate_map(self):
        return True

    def add_types(self):
        self._formatter.format_types(
                ['osd', 'node', 'zone', 'storage_group', 'root'])

    def add_devices(self):
        self._formatter.format_devices(self._osdtree.get_osds_names())

    def add_hosts_osds(self):
        names = self._osdtree.get_hosts_names()
        for h, g, z in itertools.product(names, self._storage_groups, self._zones):
            entity_name = '_'.join((h, g, z))
            # Check whether node is mapped to specified storage group and zone.
            if not self._is_mapped(g, z, h):
                items = []
            else:
                items = [(osdname, 1.0) for osdname in self._osdtree.get_osd_names_by_host(h)]
            self._formatter.format_bucket('host', entity_name,
                    self._get_bucket_num(), items)

    def add_root(self):
        items = [(i, self._get_tree_weight(i)) for i in self._storage_groups]
        self._formatter.format_bucket('root', 'vsm',
                self._get_bucket_num(), items)

    def add_storage_groups(self):
        for storage_group in self._storage_groups:
            items = []
            for zone in self._zones:
                name = '_'.join((zone, storage_group))
                weight = self._get_tree_weight(storage_group, zone)
                items.append([name, weight])
            self._formatter.format_bucket('storage_group', storage_group,
                    self._get_bucket_num(), items)

    def add_zones(self):
        for z, g in itertools.product(self._zones, self._storage_groups):
            entity_name = '_'.join((z, g))
            items = []
            for h in self._osdtree.get_hosts_names():
                weight = self._get_tree_weight(g, z, h)
                item = '_'.join([h, g, z])
                items.append([item, weight])
            self._formatter.format_bucket('zone', entity_name,
                    self._get_bucket_num(), items)

    def add_rulesets(self):
        for group in self._storage_groups:
            self._formatter.format_multiline_section('rule', group,
                    *self._get_ruleset_item(group))

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
        conv.add_root()
        conv.add_rulesets()
        print(formatter.get_content())
    pass
