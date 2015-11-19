#
# This file is part of Lab #1 of The Principles of Modern Game AI.
# Copyright (c) 2015, Victor Zarubkin.
#

__author__ = 'Victor Zarubkin'
__email__ = 'v.s.zarubkin@gmail.com'


class DoorState(object):

    CLOSED = 0
    OPEN = 1

    @staticmethod
    def to_str(state):
        if state not in (DoorState.CLOSED, DoorState.OPEN):
            return ''

        if state == DoorState.CLOSED:
            return 'closed'

        return 'open'


class Door(object):

    def __init__(self, rooms, name=''):
        object.__init__(self)
        self._name = name
        self._state = DoorState.CLOSED
        self._rooms = rooms

    def name(self):
        return self._name

    def state(self):
        return self._state

    def set_state(self, state):
        if state in (DoorState.CLOSED, DoorState.OPEN):
            self._state = state

    def between(self):
        return self._rooms


class Room(object):

    def __init__(self, name):
        object.__init__(self)
        self._name = name
        self._transitions = {}
        self._doors = []

    def name(self):
        return self._name

    def add_door(self, door):
        success = False
        for room_name in door.between():
            if room_name != self._name:
                self._add_transition(room_name, door.name())
                success = True
        if success:
            self._doors.append(door.name())

    def _add_transition(self, to_room, through_door):
        if to_room in self._transitions:
            self._transitions[to_room].append(through_door)
        else:
            self._transitions[to_room] = [through_door]

    def possible_transitions(self):
        return self._transitions

    def get_doors(self, to_room=None):
        if to_room is None:
            return self._doors
        return self._transitions.get(to_room, [])


class Map(object):

    def __init__(self):
        object.__init__(self)
        self._rooms = {}
        self._doors = {}

    def add_room(self, name):
        if name and name not in self._rooms:  # Every room must have a name and must be unique
            self._rooms[name] = Room(name)
            return True
        return False

    def add_rooms(self, rooms):
        for room in rooms:
            self.add_room(room)

    def add_door(self, door_name, room1, room2):
        if not door_name or door_name in self._doors:  # Every door must have a name and must be unique
            return False
        if room1 not in self._rooms or room2 not in self._rooms:
            return False  # Can not create transition because there is no specified room on the map
        door = Door((room1, room2), door_name)
        self._doors[door_name] = door
        self._rooms[room1].add_door(door)
        self._rooms[room2].add_door(door)

    def get_room(self, name):
        return self._rooms.get(name, None)

    def get_door(self, name):
        return self._doors.get(name, None)

