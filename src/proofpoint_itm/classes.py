import copy
import logging


class Predicate:
    """
    An class representing a Proofpoint ITM Predicate
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)

        self.definition = data.get('definition', {})
        self.patterns = data.get('patterns', [])
        self.predicates = data.get('predicates', [])
        self.purposes = data.get('purposes', [])
        self.lists = data.get('lists', [])
        self.tags = data.get('tags', [])
        self.details = data.get('details', {})
        self.alias = data.get('alias')
        self.risk = data.get('risk', {})
        self.kind = data.get('kind')
        self.refs = []
        for v in self.definition.values():
            self._get_nested_refs(v)

    def _get_nested_refs(self, data):
        for item in data:
            for k, v in item.items():
                if k == '$ref':
                    logging.info(f'found ref: {v}')
                    self.refs.append(item)
                elif k == '$not':
                    for m, n in v.items():
                        if m == '$ref':
                            logging.info(f'found ref: {n}')
                            self.refs.append(v)
                elif k == '$and' or k == '$or':
                    self._get_nested_refs(v)


class Rule:
    """
    An class representing a Proofpoint ITM Rule
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.predicate = data.get('predicate', {})
            self.actions = data.get('actions', [])
            self.options = data.get('options', [])
            self.tags = data.get('tags', [])
            self.details = data.get('details', {})
            self.alias = data.get('alias')
            self.status = data.get('status')
            self.kind = data.get('kind')
        except Exception as e:
            print(f'Error creating rule object: {e}')


class Tag:
    """
    An class representing a Proofpoint ITM Tag
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.status = data.get('status')
            self.name = data.get('name')
            self.alias = data.get('alias')
            self.details = data.get('details', {})
        except Exception as e:
            print(f'Error creating rule object: {e}')

class Policy:
    """
    An class representing a Proofpoint ITM Agent Policy
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.policy = data.get('policy', {})
            self.alias = data.get('alias')
            self.kind = data.get('kind')
            self.settings = data.get('settings')
            self.encrypt = data.get('encrypt', False)
        except Exception as e:
            print(f'Error creating rule object: {e}')

class TargetGroup:
    """
    An class representing a Proofpoint ITM Target-Group
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.displayName = data.get('displayName')
            self.description = data.get('description', '')
            self.alias = data.get('alias')
            self.targets = data.get('targets', [])
            self.purposes = data.get('purposes', [])
        except Exception as e:
            print(f'Error creating rule object: {e}')

class Target:
    """
    An class representing a Proofpoint ITM notification target
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.template = data.get('template', {})
            self.details = data.get('details', {})
            self.relations = data.get('relations', [])
            self.kind = data.get('kind')
            self.status = data.get('status')
        except Exception as e:
            print(f'Error creating rule object: {e}')