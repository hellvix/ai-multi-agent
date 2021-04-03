

class State(object):
    def __init__(self):
        pass
    
    def is_applicable(self, agent: 'Agent', action: 'Action') -> 'bool':
        pass

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass

    def is_location_free(self, location: 'Location') -> 'bool':
        pass