"""
Module responsible for managing inventory of goods.

Module class Goods is meant to be used both for global game supply,
as well as individual player's supply(ies).
"""

# TODO: maybe make this a typed dict? or at least sub categories and use parent cls as a mixin?

from typing import Self

class Goods:
    """
    Goods class.
    """
    def __new__(cls) -> Self:
        self = super().__new__(cls)
        return self
    
