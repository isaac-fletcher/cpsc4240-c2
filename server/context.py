# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

import random
from typing import Any
from collections import deque

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"


def _random_id() -> str:
    return "".join(random.choices(ALPHABET, k=10))


class Command:
    """
    Strong type wrapper around a command meant for execution 
    """

    @staticmethod
    def read(file_path: str) -> "Command":
        return Command("read", file_path, [])

    @staticmethod
    def write(file_path: str, data: str) -> "Command":
        return Command("write", file_path, [data])

    @staticmethod
    def execute(interpreter: str, args: list[str]) -> "Command":
        return Command("execute", interpreter, args)

    def __init__(self, action: str, path: str, payload: str | list[str]) -> None:
        self.action = action
        self.path = path
        self.payload = payload

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "path": self.path,
            "payload": self.payload
        }


class GlobalContext:
    """
    Manages the list of commands for each bot to execute, and keeps track
    of all known bots.
    """
    _known_bots: dict[str, deque]
    _commands_given: int
    _commands_executed: int

    def __init__(self):
        self._known_bots = {}
        self._commands_given = 0
        self._commands_executed = 0

    def create_bot(self) -> str:
        """
        Creates a new bot with an empty command queue in the store, and
        returns an ID that uniquely identifies this new bot.
        """
        new_id = _random_id()

        while new_id in self._known_bots:
            new_id = _random_id()

        self._known_bots[new_id] = deque()

        return new_id

    def command_all(self, command: Command) -> None:
        """
        Adds a command to the end of the command queue for every known bot.
        """
        for queue in self._known_bots.values():
            self._commands_given += 1
            queue.append(command)

    def command_one(self, id: str, command: Command) -> bool:
        """
        Adds a command to the end of the command queue for one single bot.
        """
        if id in self._known_bots:
            self._commands_given += 1
            self._known_bots[id].append(command)

            return True

        return False

    def extract_commands(self, id: str) -> list[Command] | None:
        """
        Empties the command queue for one bot, and returns the commands
        that were in the queue as a list (in the order they should be executed).
        """
        if id not in self._known_bots:
            return None

        result = []
        queue = self._known_bots[id]

        while len(queue) != 0:
            self._commands_executed += 1
            result.append(queue.popleft())

        return result

    def known_bots(self) -> int:
        """
        Gets the total number of bots that the server is aware of
        """
        return len(self._known_bots)

    def commands_given(self) -> int:
        """
        Gets the total number of commands that have been queued
        """
        return self._commands_given

    def commands_executed(self) -> int:
        """
        Gets the total number of commands that have been 'dispensed' to bots
        """
        return self._commands_executed
