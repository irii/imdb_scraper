from typing import Tuple

# Simple level based queue
class ScraperQueue:
    """This is a simple level based queue for prioritizing specific items.
    """
    _max_priority: int = 0
    _level_queue_dict: dict = {}

    _count: int = 0
    _total_count_dict: dict = {}

    def getMaxLevelQueue(self) -> int:
        """Returns the lowest priority level. (A high value, means low priority)

        Returns:
            int: Max level
        """
        return self._max_priority

    def getTotalCount(self, level:int=None) -> int:
        """Returns the total count of all time enqueued items. 

        Args:
            level (int, optional): Max level. Defaults to None.

        Returns:
            int: Total count based on the given level
        """
        if level == None:
            return sum(self._total_count_dict.values())


        total_sum = 0
        for r in range(0, level):
            if r in self._total_count_dict.keys():
                total_sum = total_sum + self._total_count_dict[r]

        return total_sum

    def getLength(self) -> int:
        """Returns the number of currently enqueued items.

        Returns:
            int: Count
        """
        return self._count

    def dequeue(self) -> Tuple[str, int]:
        """Dequeues a item.

        Returns:
            Tuple[str, int]: Item
        """
        for i in range(self._max_priority):
            if len(self._level_queue_dict[i]) > 0:
                self._count = self._count - 1
                return (self._level_queue_dict[i].pop(0), i + 1)

        return None

    def enqueue(self, link, priority):
        """Enqueues a item based on the priority.

        Args:
            link ([type]): [description]
            priority ([type]): [description]
        """
        if self._max_priority < priority:
            for i in range(self._max_priority, priority):
                self._level_queue_dict[i] = []
                self._total_count_dict[i] = 0

            self._max_priority = priority

        self._level_queue_dict[priority - 1].append(link)
        self._count = self._count + 1
        self._total_count_dict[priority - 1] = self._total_count_dict[priority - 1] + 1