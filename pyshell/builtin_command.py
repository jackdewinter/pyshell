from abc import ABC, abstractmethod
from typing import List


class BuiltinCommand(ABC):
    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        return self.__name

    @abstractmethod
    def execute_command(self, arguments: List[str], stdout, stderr):
        pass
