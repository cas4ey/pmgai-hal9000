#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.

import window                   # Terminal input and display.

from datetime import datetime

import nltk  # Chat-bot

from map import Map, DoorState


class HAL9000(object):

    _greetings = [
        "Good ${daytime}! This is HAL.",
        "Hello.",
        "Good ${daytime}."
    ]

    _default_responses = [
        'I\'m sorry, I can\'t understand you...',
        'I can\'t recognize your request. Please, rephrase your question.',
        'Yeah, that\'s fine... Stop mumbling, please!',
        'Can you be more exact in your requests?',
        'Please, remember that I am an Artificial Intelligence! And sometimes I can be more artificial than '
        'intelligent...'
    ]

    _responses = [
        (r'^(hal|hey you)?[\.\!\s]$', ['Yes?', 'HAL9000 is listening.', 'HAL on line.', 'What?']),
        (r'(hi|hello|hey)[\,\s\.\!]*', _greetings),
        (r'good (morning|day|evening|night)', _greetings),
        (r'where am i\?*', ['You are in the ${location} now.']),
        (r'(ok|o\.k\.|fine|excellent|cool)', ['Good.', 'Do you think so?', 'Awesome.', 'Perfect.']),
        (r'(really|are you serious)\?', ['Of course!', 'Sure!', 'Yes!', 'Absolutely.']),
        (r'([\w\s]+)', ['What do you mean by saying \'%1\'?'] + _default_responses),
        (r'', _default_responses)
    ]
    
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self._terminal = terminal
        self._map = Map()
        self._create_map()
        self._location = self._map.get_room('start location')
        self._chatbot = nltk.chat.Chat(HAL9000._responses, nltk.chat.util.reflections)
        self._commands = {
            'quit': lambda x: vispy.app.quit(),
            'open': self._try_to_open_door,
            'close': self._try_to_close_door,
            'goto': self._try_to_relocate,
            'relocate': self._try_to_relocate,
            'where': self._print_where,
            'transitions': self._print_possible_transitions
        }

    def _create_map(self):
        self._map.add_rooms(('start location', 'main corridor', 'kitchen', 'store', 'command post', 'bathroom',
                             'engineering module', 'ventilating trunk'))

        self._map.add_door('gate 1', 'start location', 'main corridor')
        self._map.add_door('engineering hatch', 'start location', 'engineering module')
        self._map.add_door('vent flap 1', 'start location', 'ventilating trunk')

        self._map.add_door('gate 2', 'main corridor', 'command post')
        self._map.add_door('gate 3', 'main corridor', 'engineering module')
        self._map.add_door('gate 4', 'main corridor', 'kitchen')
        self._map.add_door('gate 5', 'main corridor', 'bathroom')

        self._map.add_door('vent flap 2', 'ventilating trunk', 'command post')
        self._map.add_door('vent flap 3', 'ventilating trunk', 'engineering module')
        self._map.add_door('vent flap 4', 'ventilating trunk', 'kitchen')
        self._map.add_door('vent flap 5', 'ventilating trunk', 'bathroom')
        self._map.add_door('vent flap 6', 'ventilating trunk', 'store')

        self._map.add_door('small door', 'kitchen', 'store')

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        player_input = evt.text.lower().replace('i\'m', 'i am')
        output = self._chatbot.respond(player_input)
        if '${daytime}' in output:
            output = output.replace('${daytime}', self._get_current_day_time_string())
        if '${location}' in output:
            output = output.replace('${location}', self._location.name())
        self._terminal.log(output, align='right', color='#00805A')

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        words = evt.text.split()
        if words and words[0] in self._commands:
            execute_command = self._commands[words[0]]
            attribute = ' '.join(words[1:]).lower()
            execute_command(attribute)

        else:
            self._terminal.log('Command \'{}\' unknown.'.format(evt.text), align='left', color='#ff3000')
            self._terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass

    def _print_where(self, where):
        if not where:
            output = self._chatbot.respond('where am i?').replace('${location}', self._location.name())
            self._terminal.log(output, align='right', color='#00805A')
            return

        if where in self._location.get_doors():
            door = self._map.get_door(where)
            to = []
            for room_name in door.between():
                if room_name != self._location.name():
                    to.append(room_name)
            self._terminal.log('{} is leading to the {}'.format(where[:1].upper() + where[1:], ', '.join(to)),
                               align='right', color='#00805A')
            return

        if where in self._location.possible_transitions():
            doors = self._location.possible_transitions()[where]
            self._terminal.log('You can get to the {} through {}'.format(where, ', '.join(doors)),
                               align='right', color='#00805A')
            return

        if where == self._location.name():
            self._print_possible_transitions()
            return

        self._terminal.log('Hm... There is no {} near the {}.'.format(where, self._location.name()),
                           align='right', color='#00805A')

    def _print_possible_transitions(self, _):
        self._terminal.log('From {} you can go:'.format(self._location.name()), align='right', color='#00805A')
        for room_name, doors in self._location.possible_transitions().items():
            self._terminal.log('- to the {} through {}.'.format(room_name, ', '.join(doors)), align='right',
                               color='#00805A')

    def _try_to_relocate(self, location_name):
        if not location_name:
            self._terminal.log('Where do you want to go?', align='right', color='#00805A')
            for room_name in self._location.possible_transitions():
                self._terminal.log('- {}.'.format(room_name), align='right', color='#00805A')
            return

        new_location = self._map.get_room(location_name)
        if new_location is None:
            self._terminal.log('Location \'{}\' unknown.'.format(location_name), align='left', color='#ff3000')
            self._terminal.log('There is no {} on the ship.'.format(location_name), align='right', color='#00805A')

        elif location_name != self._location.name():
            doors = self._location.get_doors(location_name)
            if doors:
                for door_name in doors:
                    door = self._map.get_door(door_name)
                    if door.state() == DoorState.OPEN:
                        self._location = new_location
                        self._terminal.log('', align='center', color='#404040')
                        self._terminal.log('\u2014 Now in the {}. \u2014'.format(location_name), align='center',
                                           color='#404040')
                        return
                self._terminal.log('I\'m afraid all doors to the {} are closed.'.format(location_name), align='right',
                                   color='#00805A')
                self._terminal.log('You have to open one of these doors: {}'.format(', '.join(doors)), align='right',
                                   color='#00805A')

            else:
                self._terminal.log('I\'m afraid you can\'t relocate to the {} from your current location.'
                                   .format(location_name), align='right', color='#00805A')

        else:
            self._terminal.log('You are already in the {}!'.format(location_name), align='right', color='#00805A')

    def _try_to_open_door(self, door_name):
        self._try_to_operate_door(door_name, DoorState.OPEN)

    def _try_to_close_door(self, door_name):
        self._try_to_operate_door(door_name, DoorState.CLOSED)

    def _try_to_operate_door(self, door_name, new_state):
        doors = self._location.get_doors()
        if not door_name:
            self._terminal.log('Which door do you want to open?', align='right', color='#00805A')
            for door_name in doors:
                self._terminal.log('- {}.'.format(door_name), align='right', color='#00805A')
            return

        if door_name not in doors:
            self._terminal.log('I\'m afraid there is no {} in the {}.'.format(door_name, self._location.name()),
                               align='right', color='#00805A')
            return

        state_name = DoorState.to_str(new_state)
        door = self._map.get_door(door_name)
        if door.state() == new_state:
            self._terminal.log('The {} already {}.'.format(door_name, state_name), align='right', color='#00805A')
            return

        self._terminal.log('The {} is now {}.'.format(door_name, state_name), align='right', color='#00805A')
        door.set_state(new_state)

    @staticmethod
    def _get_current_day_time_string():
        current_hour = datetime.now().hour
        if current_hour < 5 or current_hour > 22:
            return 'night'
        if current_hour < 12:
            return 'morning'
        if current_hour < 17:
            return 'day'
        return 'evening'


class Application(object):
    
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()
        
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
