import sys
import time
import logging

import cProfile

import memory
from level import Level
from color import Color
from configuration import Configuration
from controller import Controller


log = logging.getLogger(__name__)


class Client(object):
    @staticmethod
    def parse_level(server_messages) -> 'Configuration':
        log.debug("Parsing messages from server...")
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        server_messages.readline() # #domain
        server_messages.readline() # hospital
        
        # Read Level name.
        server_messages.readline() # #levelname
        __name = server_messages.readline() # <name>
        
        log.debug("Map name is: %s" % __name.replace("\n", ''))
        
        # Read colors.
        server_messages.readline() # #colors
        
        agent_colors = [None for _ in range(10)]
        box_colors = [None for _ in range(26)]
        line = server_messages.readline()
        while not line.startswith('#'):
            split = line.split(':')
            color = Color.from_string(split[0].strip())
            entities = [e.strip() for e in split[1].split(',')]
            for e in entities:
                if '0' <= e <= '9':
                    agent_colors[ord(e) - ord('0')] = color
                elif 'A' <= e <= 'Z':
                    box_colors[ord(e) - ord('A')] = color
            line = server_messages.readline()
        
        # Read initial state.
        # line is currently "#initial".
        num_rows = 0
        num_cols = 0
        level_lines = []
        line = server_messages.readline()
        
        while not line.startswith('#'):
            level_lines.append(line)
            num_cols = max(num_cols, len(line) - 1)
            num_rows += 1
            line = server_messages.readline()

        num_agents = 0
        agent_rows = [None for _ in range(10)]
        agent_cols = [None for _ in range(10)]
        walls = [[False for _ in range(num_cols)] for _ in range(num_rows)]
        boxes = [['' for _ in range(num_cols)] for _ in range(num_rows)]
        row = 0
        
        for line in level_lines:
            for col, c in enumerate(line):
                if '0' <= c <= '9':
                    agent_rows[ord(c) - ord('0')] = row
                    agent_cols[ord(c) - ord('0')] = col
                    num_agents += 1
                elif 'A' <= c <= 'Z':
                    boxes[row][col] = c
                elif c == '+':
                    walls[row][col] = True
            
            row += 1
        del agent_rows[num_agents:]
        del agent_rows[num_agents:]
        
        # Read goal state.
        # line is currently "#goal".
        goals = [['' for _ in range(num_cols)] for _ in range(num_rows)]
        line = server_messages.readline()
        row = 0
        while not line.startswith('#'):
            for col, c in enumerate(line):
                if '0' <= c <= '9' or 'A' <= c <= 'Z':
                    goals[row][col] = c
            
            row += 1
            line = server_messages.readline()
        
        # End.
        # line is currently "#end".
        log.debug("Finished parsing messages from server.")
        return Configuration({
            'walls': walls,
            
            # Boxes
            'boxes': boxes,
            'box_colors': box_colors,
            
            # Agents
            'agents': [agent_rows, agent_cols],
            'agent_colors': agent_colors,
            
            'goals': goals
        })

    @staticmethod
    def boot_up() -> None:
        # Send client name to server.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='ASCII')
        print('WESDONK', flush=True)
        
        log.debug("Sending client name to server...")
        
        # Parse the level.
        server_messages = sys.stdin
        if hasattr(server_messages, "reconfigure"):
            server_messages.reconfigure(encoding='ASCII')
        
        # Client returns raw data from the server
        configuration = Client.parse_level(server_messages)
        
        __debug_msg = 'Initializing controller...'
        print(__debug_msg, file=sys.stderr, flush=True)
        log.debug(__debug_msg)
        
        controller = Controller(configuration)
        controller.deploy()
        sys.exit(0)
                
    @staticmethod
    def send_to_server(actions: [['Actions', ...], ...]) -> None:
        """Send actions to the server. Must be already formatted.
        """
        server_messages = sys.stdin
            
        for joint_action in actions:
            print("|".join(a.name_ for a in joint_action), flush=True)
            # We must read the server's response to not fill up the stdin buffer and block the server.
            response = server_messages.readline()
