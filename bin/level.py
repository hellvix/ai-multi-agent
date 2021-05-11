import logging
import sys
import numpy as np

from copy import deepcopy

from location import Location
from action import Action, ActionType


log = logging.getLogger(__name__)


class Level(object):
    """A redifined definition of a level
    Defines locations as a a set of locations, together with its neighbors.
    """

    def __init__(self, layout: '[[Location, ...], ...]', num_rows: int, num_cols: int):
        # Representation of the level in Location objects, ignoring outside walls.
        # This means row 1 in the level is actually located in row 0 in this array.
        # [
        #   [L1,1, L1,2, L1,3],
        #   [L2,1, L2,2, ... ]
        # ]

        self.__layout = layout
        self.__num_rows = num_rows  # Total number of rows (counting outside walls)
        self.__num_cols = num_cols  # Total number of cols (counting outside walls)        
        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            prime = 37
            _hash = 1
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.__layout))
            _hash = _hash * prime + hash((self.__num_rows, self.__num_cols))
            self._hash = _hash
        return self._hash
    
    def clone(self):
        """Return a deep copy of the object
        """
        return deepcopy(self)
    
    def __repr__(self):
        return str(self.__layout)
        
    @property
    def layout(self):
        return self.__layout
    
    def update_layout(self, layout):
        self.__layout = layout

    @property
    def num_rows(self):
        return self.__num_rows
    
    @property
    def real_num_rows(self):
        """Number of rows ignoring outside walls

        Returns:
            int: number of rows
        """
        return self.num_rows - 2
    
    @property
    def num_cols(self):
        return self.__num_cols

    @property
    def real_num_cols(self):
        """Number of cols ignoring outside walls

        Returns:
            int: number of cols
        """
        return self.num_cols - 2
    
    def get_location(self, indexes: tuple, translate=False) -> Location:
        """Given the coordinates (row, col), which object location is at this position?
        Important: the layout vector is 0-indexed, this means L1,1 is located in [0][0]
        and L2,3 is located in [1][2]
        
        If translate is True, then the indexes are converted to 0-based indexes.

        Args:
            coordinates (tuple): (row, col)
            translate (bol): whether the coordinates are 0-index-based or not

        Returns:
            Location: object at this index
        """
        row, col = indexes
        try:
            if translate:
                row = row - 1
                col = col - 1
            
            if 0 > row or row > self.real_num_rows:
                raise Exception(
                    "Invalid row index row %d. Maybe use parameter translate?" % row
                )
                
            if 0 > col or col > self.real_num_cols:
                raise Exception(
                    "Invalid row index col %d. Maybe use parameter translate?" % col
                )
            
            return self.__layout[row][col]
        except IndexError:
            raise Exception(
                "Location in row %d col %d do not exist. Maybe use parameter translate?" % (row, col)
            )
        
    def location_from_action(self, location: Location, action: Action, execute=False):
        """If we apply an action in a specific location, which locations do we get in return?

        Args:
            location (Location): location where we start
            action (Action): Move, Pull or Push
            execute (bool): If true, return the location as if the action was executed
            
        Returns:
            Location(s): if action is either Push or Pull, 
            we return Tuple(Agent Location, Box Location), otherwise Agent Location
        """
        
        _arow = location.row + action.agent_row_delta # Y
        _acol = location.col + action.agent_col_delta # x
        _apos = None
        _bpos = None
        
        if action.type is ActionType.NoOp:
            return location
        
        # Where agent will be
        if action.type is ActionType.Move:
            return self.get_location((_arow, _acol), translate=True)

        # Box position
        else:
            if action.type is ActionType.Pull:
                if not execute:
                    # The inverse of where the box is supposed to be === where the box is
                    # We want this location to know if there is a box there
                    _brow = location.row + action.box_row_delta * -1
                    _bcol = location.col + action.box_col_delta * -1
                else:
                    _brow = location.row
                    _bcol = location.col
            else:
                _brow = _arow + action.box_row_delta
                _bcol = _acol + action.box_col_delta
            
            try:
                _apos = self.get_location((_arow, _acol), translate=True)  # Agent position
            except Exception:
                pass

            try:
                _bpos = self.get_location((_brow, _bcol), translate=True)   # Box position
            except Exception:
                pass
            
            return _apos, _bpos
        raise Exception('Could not define location.')
