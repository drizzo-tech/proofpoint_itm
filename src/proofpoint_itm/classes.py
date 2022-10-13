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
    
    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new predicate
        """
        data = {
            'definition': self.definition,
            'patterns': self.patterns,
            'predicates': self.predicates,
            'purposes': self.purposes,
            'lists': self.lists,
            'tags': self.tags,
            'details': self.details,
            'alias': self.alias,
            'risk': self.risk,
            'kind': self.kind
        }
        return data


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

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new rule
        """
        data = {
            'predicate': self.predicate,
            'actions': self.actions,
            'options': self.options,
            'tags': self.tags,
            'details': self.details,
            'alias': self.alias,
            'status': self.status,
            'kind': self.kind
        }
        return data

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
    
    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new tag
        """
        data = {
            'status': self.status,
            'name': self.name,
            'alias': self.alias,
            'details': self.details,
        }
        return data

class AgentPolicy:
    """
    An class representing a Proofpoint ITM Agent Policy
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.alias = data.get('alias')
            self.description = data.get('description')
            self.kind = data.get('kind')
            self.refs = data.get('refs', {'rules': {'rules': []}})
            self.match = data.get('match', {})
            self.settings = data.get('settings', {})
            self.encrypt = data.get('encrypt', False)
            self.deleted = data.get('deleted', False)
            self.priority = data.get('priority', '-1')
        except Exception as e:
            print(f'Error creating agent policy object: {e}')

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new policy
        """
        data = {
            'description': self.description,
            'match': self.match,
            'settings': self.settings,
            'alias': self.alias,
            'kind': self.kind,
            'refs': self.refs,
            'encrypt': self.encrypt,
            'deleted': self.deleted,
            'priority': self.priority
        }
        return data

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
            self.extent = data.get('extent', 'tenant')
        except Exception as e:
            print(f'Error creating rule object: {e}')

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new target-group
        """
        data = {
            'displayName': self.displayName,
            'description': self.description,
            'targets': self.targets,
            'purposes': self.purposes,
            'alias': self.alias,
            'extent': self.extent
        }
        return data

class Target:
    """
    A class representing a Proofpoint ITM notification target
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.details = data.get('details', {})
            self.relations = data.get('relations', [])
            self.kind = data.get('kind')
            self.status = data.get('status')
        except Exception as e:
            print(f'Error creating rule object: {e}')

        try:
            self.template = data['template']
        except KeyError:
            pass

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new target
        """
        data = {
            'relations': self.relations,
            'details': self.details,
            'status': self.status,
            'kind': self.kind
        }
        try:
            data['template'] = self.template
        except:
            pass

        return data

class Dictionary:
    """
    A class representing a Proofpoint ITM dictionary
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.name = data.get('name')
            self.description = data.get('description')
            self.entries = data.get('entries', [])
        except Exception as e:
            print(f'Error creating dictionary object: {e}')

        try:
            self.category = data['category']['id']
        except KeyError:
            print(f'Could not find category id for dictionary: {self.name}')
    
    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new dictionary
        """
        data = {
            'name': self.name,
            'description': self.description,
            'entries': self.entries
        }
        
        try:
            data['category'] = self.category
        except:
            pass
        
        return data

class Detector:
    """
    A class representing a Proofpoint ITM detector
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.name = data.get('name')
            self.description = data.get('description')
            self.expression = data.get('expression')
            self.dictionaries = data.get('dictionaries', [])
            self.smartIds = data.get('smartIds', [])
        except Exception as e:
            print(f'Error creating dictionary object: {e}')

        try:
            self.category = data['category']['id']
        except KeyError:
            print(f'Could not find category id for detector: {self.name}')

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new detector
        """
        data = {
            'name': self.name,
            'description': self.description,
            'expression': self.expression,
            'dictionaries': self.dictionaries,
            'smartIds': self.smartIds
        }

        try:
            data['category'] = self.category
        except:
            pass

        return data


class DetectorSet:
    """
    A class representing a Proofpoint ITM detector set
    """
    def __init__(self, json_data={}):
        data = copy.deepcopy(json_data)
        try:
            self.name = data.get('name')
            self.description = data.get('description')
            detectors = data.get('enabledDetectors', [])
            enabledDetectors = []
            for detector in detectors:
                enabledDetectors.append(detector['id'])
            self.enabledDetectors = enabledDetectors
            #self.dictionaries = data.get('dictionaries', [])
            #self.smartIds = data.get('smartIds', [])
        except Exception as e:
            print(f'Error creating dictionary object: {e}')

        try:
            self.category = data['category']['id']
        except KeyError:
            print(f'Could not find category id for detector: {self.name}')

    def as_dict(self):
        """
        Returns a dict object with only the keys needed to create a new detector
        """
        data = {
            'name': self.name,
            'description': self.description,
            'enabledDetectors': self.enabledDetectors,
        }

        try:
            data['category'] = self.category
        except:
            pass

        return data