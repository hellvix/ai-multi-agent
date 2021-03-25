import numpy as np
from box import Box
from agent import Agent
from level import Level
from color import Color
from location import Location
from enum import Enum, unique


@unique
class RaceType(Enum):
    BOXES = 0
    AGENTS = 1


class Configuration(object):
    def __init__(self, raw_data: dict):
        
        # Configuration type: only agents? boxes?
        self.__type = RaceType.AGENTS
        
        # Walls
        self.__raw_walls = raw_data['walls']
        
        # Boxes
        self.__raw_boxes = raw_data['boxes']
        self.__raw_box_colors = raw_data['box_colors']
        
        # Agents
        self.__raw_agents = raw_data['agents']
        self.__raw_agent_colors = raw_data['agent_colors']
        
        # Goals
        self.__raw_goals = raw_data['goals']

        
    @property
    def race_type(self):
        """The type of challenge we are dealing with.

        Returns:
            RaceType: type of level (boxes or agents)
        """
        return self.__type
    
    def build_goals(self) -> dict:
        _raw_goals = self.__raw_goals
        
        _goals = {}
        
        for row in range(1, self.level_row_cnt - 1):
            for col in range(1, self.level_col_cnt - 1):
                p_goal = _raw_goals[row][col]
                
                if p_goal:
                    _goals.update({
                        p_goal: Location(row, col)
                    })
                    
        return _goals
    
    def build_agents(self) -> '[Agent, ...]':
        # Raw
        _agent_rows = self.__raw_agents[0]
        _agent_cols = self.__raw_agents[1]
        _agent_colors = self.__raw_agent_colors
        
        _agents = np.array([])
        
        # Every index represents an agent in in _agent_rows
        for a_id, a_row in enumerate(_agent_rows):
            a_col = _agent_cols[a_id]
            a_loc = Location(a_row, a_col)
            a_color = Color(_agent_colors[a_id])
            
            _agents = np.append(_agents, Agent(a_id, a_loc, a_color))

        return _agents
    
    def build_boxes(self) -> '[Box, ...]':
               
        # Raw
        _box_positions = self.__raw_boxes
        _box_colors = self.__raw_box_colors
        
        _boxes = np.array([])
        
        for row in range(1, self.level_row_cnt - 1):
            for col in range(1, self.level_col_cnt - 1):
                p_box = _box_positions[row][col]
                
                if p_box:
                    c_box = ord(p_box) - ord('A')
                    b_color = _box_colors[c_box]
                    b_loc = Location(row, col)
                    _boxes = np.append(_boxes, Box(p_box, b_loc, b_color))
        
        # Change configuration type
        if _boxes.any(): self.__type = RaceType.BOXES

        return _boxes
        
    def build_level(self):
        """Builds an adjacent list with locations and its neighbors
        """
        raw_walls = self.__raw_walls
        self.level_row_cnt = row_cnt = len(raw_walls)
        self.level_col_cnt = col_cnt = len(raw_walls[0])
        
        # Ignoring out of bound walls
        layout = np.array([
            [Location(row, col) for col in range(1, col_cnt - 1)] for row in range(1, row_cnt - 1)
        ])

        for entries in layout:
            for loc in entries:
                crow = loc.row
                ccol = loc.col
                loc.is_wall = raw_walls[crow][ccol]

                # We don't generate neighbors for walls
                if not loc.is_wall:
                    # Possible neigbohood locations
                    positions = (
                        (crow + 1, ccol),  # north
                        (crow - 1, ccol),  # south
                        (crow, ccol + 1),  # east
                        (crow, ccol - 1),  # west
                    )

                    # Positions in the location array start from 0
                    # Ignoring walls
                    loc.neighbors = set(
                        layout[nrow-1][ncol-1] for nrow, ncol in positions if not raw_walls[nrow][ncol]
                    )
        return Level(layout, row_cnt, col_cnt)
