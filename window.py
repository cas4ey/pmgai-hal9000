#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import nuclai.bootstrap         # Demonstration specific setup.
import vispy.scene              # Canvas & visuals for rendering.
import vispy.util.event         # Events and observer support.

CONSOLE_PREFIX = '> '
CONSOLE_LINEHEIGHT = 40.0
CONSOLE_LINEOFFSET = 16.0
CONSOLE_MARGIN = 16.0
MAX_BUFFER_SIZE = 64


class TextEvent(vispy.util.event.Event):
    """Simple data-structure to store a text string, as processed by the terminal window.
    """

    def __init__(self, text):
        super(TextEvent, self).__init__('text_event')
        self.text = text


class TerminalWindow(object):
    """Creates and manages a window used for terminal input. You can setup notifications via
    `self.events` that emits notifications for user inputs and user commands. 
    """

    def __init__(self):
        """Constructor sets up events, creates a canvas and data for processing input.
        """ 
        self.events = vispy.util.event.EmitterGroup(
                                user_input=TextEvent,
                                user_command=TextEvent)
 
        self._create_canvas()
        self._create_terminal()

    def _create_canvas(self):
        """Initialize the Vispy scene and a canvas, connect up the events to this object.
        """
        self.canvas = vispy.scene.SceneCanvas(
                                title='HAL9000 Terminal - nucl.ai Courses',
                                size=(1280, 720),
                                bgcolor='#F0F0F0',
                                show=False,
                                keys='interactive')
        
        self.widget = self.canvas.central_widget
        self.widget.set_transform('matrix')
        self.widget.transform.translate((0.0, -CONSOLE_LINEOFFSET))

        vispy.scene.visuals.GridLines(parent=self.widget, scale=(0.0, 15.984/CONSOLE_LINEHEIGHT))

        self.canvas.show(visible=True)
        self.canvas.events.mouse_press()            # HACK: Layout workaround for bug in Vispy 0.5.0.

        self.old_size = self.canvas.size
        self.canvas.events.resize.connect(self.on_resize)
        self.canvas.events.key_press.connect(self.on_key_press)
        self.canvas.events.key_release.connect(self.on_key_release)

    def _create_terminal(self):
        """Setup everything that's necessary for processing key events and the text.
        """
        self.text_buffer = ''
        self.entry_offset = CONSOLE_LINEOFFSET - CONSOLE_LINEHEIGHT / 2 + self.canvas.size[1] 
        self.entry_blink = 0
        self.entries = []
        self.text_log = ['']
        self.log_index = 0
        self.log_message_modified = False
        self._pressed_buttons = {}

        self._key_handlers = {
            'Enter': self._on_press_enter,
            'Backspace': self._on_press_backspace,
            'Up': self._on_press_up,
            'Down': self._on_press_down
        }

        self.log(CONSOLE_PREFIX, color='#1463A3')

        timer = vispy.app.Timer(interval=1.0 / 3.0)
        timer.connect(self.on_blink)
        timer.start()

        timer2 = vispy.app.Timer(interval=0.025)
        timer2.connect(self.on_repeat_keys)
        timer2.start()

    def scroll(self, height):
        self.widget.transform.translate((0.0, -height))

    def on_resize(self, evt):
        self.scroll(self.old_size[1] - evt.size[1])
        self.old_size = evt.size

    def log(self, text, align='left', color='#1463A3'):
        assert align in ('left', 'right', 'center')

        if align == 'center':
            position = self.canvas.size[0] / 2
        elif align == 'left':
            position = CONSOLE_MARGIN
        else:
            position = self.canvas.size[0] - CONSOLE_MARGIN

        if text != '':
            entry = vispy.scene.visuals.Text(parent=self.widget,
                                         text=text,
                                         face='Questrial',
                                         color=color,
                                         bold=False,
                                         font_size=20,
                                         anchor_x=align,
                                         anchor_y='bottom',
                                         pos=[position, self.entry_offset, 0.0])
            self.entries.append(entry)

        self.scroll(CONSOLE_LINEHEIGHT)
        self.entry_offset += CONSOLE_LINEHEIGHT
        
        self.entries[0].pos[0][1] = self.entry_offset

    def show_input(self, text):
        self.entries[0].text = CONSOLE_PREFIX + text
        self.entries[0].update()

    def on_key_press(self, evt):
        if evt.key.name not in self._pressed_buttons:
            self._pressed_buttons[evt.key.name] = [evt, 0.0]

        self._key_press_handler(evt)

    def _key_press_handler(self, evt):
        if evt.text:
            self.on_key_char(evt.text)

        c = evt.key
        handler = self._key_handlers.get(c.name, self._on_press_any)
        handler()

        self.show_input(self.text_buffer)

    def on_key_release(self, evt):
        if evt.key.name in self._pressed_buttons:
            del self._pressed_buttons[evt.key.name]

    def _on_press_enter(self):
        if self.text_buffer:
            if self.text_buffer.startswith('/'):
                self.events.user_command(TextEvent(self.text_buffer[1:]))
            else:
                self.log(self.text_buffer, align='left')
                self.events.user_input(TextEvent(self.text_buffer))
            if self.log_message_modified or self.log_index != -1:
                self.text_log.append(self.text_buffer)
                if len(self.text_log) > MAX_BUFFER_SIZE:
                    self.text_log.pop(1)
            self.log_index = 0
            self.text_buffer = ''
            self.log_message_modified = False

    def _on_press_backspace(self):
        if self.text_buffer:
            self.log_message_modified = True
        self.text_buffer = self.text_buffer[:-1]

    def _on_press_up(self):
        min_index = 1 - len(self.text_log)
        if self.log_index > min_index:
            self.log_index -= 1
            self.text_buffer = self.text_log[self.log_index]
            self.log_message_modified = False

    def _on_press_down(self):
        self.log_message_modified = False
        if self.log_index < 0:
            self.log_index += 1
            self.text_buffer = self.text_log[self.log_index]
            self.log_message_modified = False

    def _on_press_any(self):
        self.log_message_modified = True

    def on_key_char(self, text):
        self.text_buffer += text
        self.show_input(self.text_buffer)

    def on_blink(self, _):
        if (self.entry_blink%2) == 0:
            self.show_input(self.text_buffer+'_')
        if (self.entry_blink%2) == 1:
            self.show_input(self.text_buffer)
        self.entry_blink += 1

    def on_repeat_keys(self, evt):
        for _, v in self._pressed_buttons.items():
            v[1] += evt.dt
            if v[1] > 0.5:
                self._key_press_handler(v[0])
