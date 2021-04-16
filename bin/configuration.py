import numpy as np
from box import Box
from goal import Goal
from agent import Agent
from level import Level
from color import Color
from location import Location
from enum import Enum, unique


@unique
class StrategyType(Enum):
    BOXES = 0
    AGENTS = 1


class Configuration(object):
    def __init__(self, raw_data: dict):
        
        # Configuration type: only agents? boxes?
        self.__type = StrategyType.AGENTS
        
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
            StrategyType: type of level (boxes or agents)
        """
        return self.__type
    
    def __build_goals(self, level: Level) -> dict:
        """Dictionary with goals. Key is goal name (A, B, 0, 1...) and value is a Location object.

        Args:
            level (Level): [description]

        Returns:
            dict: [description]
        """
        _raw_goals = self.__raw_goals
        _goals = {}
        
        for row in range(1, self.level_row_cnt - 1):
            for col in range(1, self.level_col_cnt - 1):
                gl_label = _raw_goals[row][col]
                
                if gl_label:
                    loc = level.get_location((row, col), translate=True)
                    
                    if 'A' <= gl_label <= 'Z':
                        color = Color(self.__raw_box_colors[ord(gl_label) - ord('A')])
                    elif '0' <= gl_label <= '9':
                        color = Color(self.__raw_agent_colors[ord(gl_label) - ord('0')])
                    else:
                        raise Exception('Unsupported type of goal.')
                    
                    _goals.update({
                        loc: Goal(gl_label, loc, color)
                    })

        return _goals
    
    def __build_agents(self, level: Level) -> '[Agent, ...]':
        
        # Raw
        _agent_rows = self.__raw_agents[0]
        _agent_cols = self.__raw_agents[1]
        _agent_colors = self.__raw_agent_colors
        
        _agents = np.array([])
        
        # Every index represents an agent in in _agent_rows
        for a_id, a_row in enumerate(_agent_rows):
            a_col = _agent_cols[a_id]
            a_loc = level.get_location((a_row, a_col), translate=True)
            a_color = Color(_agent_colors[a_id])
            
            _agents = np.append(_agents, Agent(a_id, a_loc, a_color))

        return _agents
    
    def __build_boxes(self, level: Level) -> '[Box, ...]':
               
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
                    b_loc = level.get_location((row, col), translate=True)
                    _boxes = np.append(_boxes, Box(p_box, b_loc, b_color))

        return _boxes
        
    def __build_level(self):
        """Builds an adjacent list with locations and its neighbors
        """
        raw_walls = self.__raw_walls
        self.level_row_cnt = row_cnt = len(raw_walls)
        self.level_col_cnt = col_cnt = len(raw_walls[0])
        
        # Ignoring out of bound walls
        #
        # Symmetric matrix with locations
        # this, however, infers storing a lot of walls in certain maps, such as MAbispebjerg.lvl
        #
        layout = np.array([
            [Location(row, col) for col in range(1, col_cnt - 1)] for row in range(1, row_cnt - 1)
        ], dtype=object)
        
        # for each row
        for entries in layout:
            # for loc in each col
            for loc in entries:
                crow = loc.row
                ccol = loc.col
                loc.is_wall = raw_walls[crow][ccol]  # Whether location is wall

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
                    try:
                        loc.neighbors = set(
                            layout[nrow-1][ncol-1] for nrow, ncol in positions if not raw_walls[nrow][ncol]
                        )
                    except IndexError:
                        pass

        return Level(layout, row_cnt, col_cnt)
    
    def build_structure(self):
        __level = self.__build_level()
        __agents = self.__build_agents(__level)
        __boxes = self.__build_boxes(__level)
        __goals = self.__build_goals(__level)
        self.__type = self.__get_race_type(__agents, __boxes, __goals)
        
        return __level, __agents, __boxes, __goals
    
    def __get_race_type(self, agents: [Agent, ...], boxes: [Box, ...], goals: [Goal, ...]):
        # Change configuration type
        if not boxes.any():
            return StrategyType.AGENTS

        all_goals = set(str(g.identifier) for loc, g in goals.items())
        
        for b in boxes:
            if b.identifier in all_goals:
                return StrategyType.BOXES
            
        for a in agents:
            if a.identifier in all_goals:
                return StrategyType.AGENTS
        
        # If reached here, we do not know the type of strategy to use
        raise Exception(
            'Could not identify level. '
            'This is mostly because this algorithm was '
            'not designed for this type level configuration.'
        )
