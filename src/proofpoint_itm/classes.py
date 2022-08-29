
class Predicate:
    """
    An class representing a Proofpoint ITM Predicate
    """
    def __init__(self, json_data={}):
        try:
            self.definition = json_data.get('definition', {})
            self.patterns = json_data.get('patterns', [])
            self.predicates = json_data.get('predicates', [])
            self.purposes = json_data.get('purposes', [])
            self.lists = json_data.get('lists', [])
            self.tags = json_data.get('tags', [])
            self.details = json_data.get('details', {})
            self.alias = json_data.get('alias')
            self.risk = json_data.get('risk', {})
            self.kind = json_data.get('kind')
        except Exception as e:
            print(f'Error creating predicate object: {e}')


class Rule:
    """
    An class representing a Proofpoint ITM Rule
    """
    def __init__(self, json_data={}):
        try:
            self.definition = json_data.get('definition', {})
            self.predicate = json_data.get('predicate', {})
            self.actions = json_data.get('actions', [])
            self.options = json_data.get('options', [])
            self.tags = json_data.get('tags', [])
            self.details = json_data.get('details', {})
            self.alias = json_data.get('alias')
            self.status = json_data.get('status')
            self.kind = json_data.get('kind')
        except Exception as e:
            print(f'Error creating rule object: {e}')


class Tag:
    """
    An class representing a Proofpoint ITM Tag
    """
    def __init__(self, json_data={}):
        try:
            self.status = json_data.get('status')
            self.name = json_data.get('name')
            self.alias = json_data.get('alias')
            self.details = json_data.get('details', {})
            self.extent = 'tenant'
        except Exception as e:
            print(f'Error creating rule object: {e}')

class Policy:
    """
    An class representing a Proofpoint ITM Agent Policy
    """
    def __init__(self, json_data={}):
        try:
            self.policy = json_data.get('policy', {})
            self.alias = json_data.get('alias')
        except Exception as e:
            print(f'Error creating rule object: {e}')