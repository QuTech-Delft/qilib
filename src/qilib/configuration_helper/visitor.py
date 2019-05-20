from abc import ABC, abstractmethod
from typing import Any


class Visitor(ABC):
    @abstractmethod
    def visit(self, element: Any)-> None:
        """ stuff"""
