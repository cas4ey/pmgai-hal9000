#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.

import window                   # Terminal input and display.

from datetime import datetime
import random


class HAL9000(object):

    _greetings = [
        "Good ${daytime}! This is HAL.",
        "Hello.",
        "Good ${daytime}."
    ]

    _error_replies = [
        'I\'m sorry, I can\'t understand you...',
        'I can\'t recognize your request.'
    ]

    _greetings_words = (
        'hi',
        'hello',
        'hey',
        'good day',
        'good morning',
        'good night',
        'good evening'
    )
    
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self._last_greeting = -1
        self._last_unknown_reply = -1

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        player_input = evt.text.lower()
        if any(s in player_input for s in HAL9000._greetings_words):
            output, self._last_greeting = self._choose_random_reply(HAL9000._greetings, self._last_greeting)
        elif 'where am i' in player_input:
            if self.location != 'unknown':
                output = 'You are in {} now.'.format(self.location)
            else:
                output = 'Hmm... I don\'t know where are you...'
        else:
            output, self._last_unknown_reply = self._choose_random_reply(HAL9000._error_replies,
                                                                         self._last_unknown_reply)
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
                self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), align='center', color='#404040')

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass

    @staticmethod
    def _choose_random_reply(possible_replies, last_reply=None):
        replies = list(range(len(possible_replies)))
        if last_reply is not None and len(replies) > 2 and last_reply in replies:
            replies.pop(last_reply)
        reply_index = random.choice(replies)
        if reply_index >= len(possible_replies) or reply_index < 0:
            reply_index = 0
        reply = possible_replies[reply_index]
        if '${daytime}' in reply:
            reply = reply.replace('${daytime}', HAL9000._get_current_day_time_string())
        return reply, reply_index

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
