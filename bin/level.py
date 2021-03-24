import sys
import heapq
import numpy as np
from location import Location


class Level(object):
    """A redifined definition of a level
    Defines locations as a a set of locations, together with its neighbors.
    """

    def __init__(self, layout: list, num_rows: int, num_cols: int):
        # Representation of the level in Location objects, ignoring outside walls.
        # This means row 1 in the level is actually located in row 0 in this array.
        # [
        #   [L1,1, L1,2, L1,3],
        #   [L2,1, L2,2, ... ]
        # ]

        self.__layout = layout
        self.__num_rows = num_rows  # Total number of rows (counting outside walls)
        self.__num_cols = num_cols  # Total number of cols (counting outside walls)
        
    @property
    def layout(self):
        return self.__layout

    @property
    def num_rows(self):
        return self.__num_rows
    
    @property
    def real_num_rows(self):
        """Number of rows ignoring outside walls

        Returns:
            int: number of rows
        """
        return self.__num_rows - 1
    
    @property
    def num_cols(self):
        return self.__num_cols

    @property
    def real_num_cols(self):
        """Number of cols ignoring outside walls

        Returns:
            int: number of cols
        """
        return self.__num_cols - 1
