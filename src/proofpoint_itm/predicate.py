
class Predicate:
    """
    An class representing a Proofpoint ITM Predicate
    """
    def __init__(self, json_data=None):
        if json_data:
            try:
                self.definition = json_data['definition']
                self.details = json_data['details']
                self.alias = json_data['alias']
                self.risk = json_data['risk']
                self.kind = json_data['kind']
            except Exception as e:
                print(f'Error creating predicate object: {e}')
        else:
            self.definition = {}
            self.details = {}
            self.alias = None
            self.risk = {}
            self.kind = None

