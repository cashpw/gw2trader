from typing import Self

class Coins():
    """Represents a combination of gold, silver, and copper coins."""

    def __init__(self, copper: int = 0, silver: int = 0, gold: int = 0):
        """Initialize a representation of gold, silver, and copper coins.

        1 gold = 100 silver = 10,000 copper

        1 silver = 100 copper

        - Coins(12345): 1 gold, 23 silver, and 45 copper
        - Coins(copper=45, silver=12): 0 gold, 12 silver, and 45 copper
        - Coins(gold=8): 8 gold, 0 silver, and 0 copper
        """

        if copper < 0 or silver < 0 or gold < 0:
            raise Exception("Cannot store negative coins.")

        if (silver == 0 and gold == 0) and copper > 0:
            self._gold, self._silver, self._copper = copper_to_gold_silver_copper(copper)
        else:
            self._gold = gold or 0
            self._silver = silver or 0
            self._copper = copper or 0

    def __repr__(self):
        """TODO"""
        return self._human_readable()

    def __str__(self):
        """TODO"""
        return self._human_readable()

    def __gt__(self, other: Self) -> bool:
        """Return true if A is > B."""

        return self.to_copper() > other.to_copper()

    def __ge__(self, other: Self) -> bool:
        """Return true if A is >= B."""

        return self.to_copper() >= other.to_copper()

    def __add__(self, other: Self) -> Self:
        """Return the sum of two Coins."""

        return Coins(self.to_copper() + other.to_copper())

    def __sub__(self, other: Self) -> Self:
        """Return the difference of two Coins."""

        return Coins(self.to_copper() - other.to_copper())

    def __mul__(self, other: int|float) -> Self:
        """Return the produt of OTHER and self."""

        return Coins(self.to_copper() * other)

    def _human_readable(self) -> str:
        """Return human-readable representation of coinage."""

        if self._gold == 0 and self._silver == 0:
            return f"{self._copper}c"

        if self._gold == 0:
            return f"{self._silver}s {self._copper:>2}c"

        return f"{self._gold}g {self._silver: >2}s {self._copper: >2}c"

    def to_copper(self) -> int:
        """Return value in copper."""

        return self._copper + (self._silver * 100) + (self._gold * 10000)

def copper_to_gold_silver_copper(copper: int) -> tuple:
    """TODO"""

    gold = copper // 10000
    silver = (copper - (gold * 10000)) // 100

    return int(gold), int(silver), int(copper - (gold * 10000) - (silver * 100))
