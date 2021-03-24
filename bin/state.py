

class State:
    def is_applicable(self, agent: 'Agent', action: 'Action') -> 'bool':
        pass

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass

    def is_free(self, location: 'Location') -> 'bool':
        pass