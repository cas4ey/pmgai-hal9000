#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.

import window                   # Terminal input and display.

from datetime import datetime

import nltk  # Chat-bot


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
        self.terminal = terminal
        self.location = 'start location'
        self._last_input = ''
        self._chatbot = nltk.chat.Chat(HAL9000._responses, nltk.chat.util.reflections)

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        self._last_input = evt.text
        player_input = self._last_input.lower()
        player_input = player_input.replace('i\'m', 'i am')
        output = self._chatbot.respond(player_input)
        if '${daytime}' in output:
            output = output.replace('${daytime}', self._get_current_day_time_string())
        if '${location}' in output:
            output = output.replace('${location}', self.location)
        self.terminal.log(output, align='right', color='#00805A')

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            new_location = evt.text[9:].lower()
            if new_location != self.location:
                self.location = new_location
                self.terminal.log('', align='center', color='#404040')
                self.terminal.log('\u2014 Now in the {}. \u2014'.format(new_location), align='center', color='#404040')
            else:
                self.terminal.log('You are already in the {}!'.format(new_location), align='right', color='#00805A')

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass

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
