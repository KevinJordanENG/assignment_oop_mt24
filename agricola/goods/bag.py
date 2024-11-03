"""
Bag module, reusable data struct for collection with item repetition but no order.

Inspired & some construct logic borrowed from Dr. Stefano Gogioso's
implementation in OOP MT 2024 course materials.
"""
from typing import Generic, TypeVar
from collections.abc import Hashable, Iterator


ItemT = TypeVar("ItemT", bound=Hashable)
"""Need items to be hashable (same name==same item) & define generic type var."""

class Bag(Generic[ItemT]):
    """Bag collection, reusable data struct for items with repetition but no order."""

    _items: dict[ItemT, int] # Contains item name and count.

    def __init__(self, item: ItemT, count: int = 1) -> None:
        """Init a new bag, cannot be empty."""
        # Empty bag init error check.
        if item is None:
            raise ValueError("Cannot create bag with no items.")
        # Empty struct alloc for new bag.
        self._items = {}
        # Add 'count' of 'item' to internal dict.
        self.add(item, count)

    def count(self, item: ItemT) -> int:
        """Counts number of 'item' present in bag."""
        # Uses dict.get() builtin optional return val = 0 for missing item.
        return self._items.get(item, 0)

    def add(self, item: ItemT, count: int = 1) -> None:
        """Adds 'count' of 'item' to bag."""
        # Error check for null(0) or negative adds.
        if count < 1:
            raise ValueError("Cannot add less than 1 item to bag.")
        self._items[item] = self.count(item) + count

    def remove(self, item: ItemT, count: int = 1) -> None:
        """Removes 'count' of 'item' from bag."""
        # Error check for null(0) or negative removal.
        if count < 1:
            raise ValueError("Cannot remove less than 1 item from bag.")
        # If asking to remove more than remaining, delete entirely from bag.
        if (current_cnt := self.count(item)) <= count:
            del self._items[item]
        else:
            self._items[item] = current_cnt - count

    def __len__(self) -> int:
        """Dunder method overwrite for getting total number of items in bag."""
        # Values in dict is int: 'count' of each item.
        return sum(self._items.values())

    def __iter__(self) -> Iterator[ItemT]:
        """
        Iterator generator allowing iteration over Bag items.
        
        The construction using yield automatically creates a generator function,
        keeping track of its iteration/paused control execution until __next__()
        item is returned to caller.
        """
        # Get key:value pairs to iterate over.
        for item, count in self._items.items():
            # Yield the 'item' for 'count' number of times while iterating.
            for _ in range(count):
                yield item
