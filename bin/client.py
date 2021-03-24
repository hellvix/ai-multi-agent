import sys
import time

import cProfile

import memory
from level import Level
from color import Color
from configuration import Configuration
from controller import Controller


class Client:
    @staticmethod
    def parse_level(server_messages) -> 'Configuration':
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        server_messages.readline() # #domain
        server_messages.readline() # hospital
        
        # Read Level name.
        server_messages.readline() # #levelname
        server_messages.readline() # <name>
        
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
    def print_search_status(start_time: 'int', explored: '{State, ...}', frontier: 'Frontier') -> None:
        status_template = '#Expanded: {:8,}, #Frontier: {:8,}, #Generated: {:8,}, Time: {:3.3f} s\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]'
        elapsed_time = time.perf_counter() - start_time
        print(status_template.format(len(explored), frontier.size(), len(explored) + frontier.size(), elapsed_time, memory.get_usage(), memory.max_usage), file=sys.stderr, flush=True)

    @staticmethod
    def boot_up() -> None:
        # Use stderr to print to the console.
        print('Client initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)
        
        # Send client name to server.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='ASCII')
        print('Client', flush=True)
        
        # Parse the level.
        server_messages = sys.stdin
        if hasattr(server_messages, "reconfigure"):
            server_messages.reconfigure(encoding='ASCII')
        
        # Client returns raw data from the server
        configuration = Client.parse_level(server_messages)
        
        # Search for a plan.
        print('Initializing controller...', file=sys.stderr, flush=True)
        
        controller = Controller(configuration)
        plan = controller.deploy()
        
        # Print plan to server.
        if plan is None:
            print('Unable to solve level.', file=sys.stderr, flush=True)
            sys.exit(0)
        else:
            print('Found solution of length {}.'.format(len(plan)), file=sys.stderr, flush=True)
            
            for joint_action in plan:
                print(";".join(a.name_ for a in joint_action), flush=True)
                # We must read the server's response to not fill up the stdin buffer and block the server.
                response = server_messages.readline()
