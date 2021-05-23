from typing import Tuple

# Simple level based queue
class ScraperQueue:
    _max_priority: int = 0
    _level_queue_dict: dict = {}

    _count: int = 0
    _total_count: int = 0

    def getMaxLevelQueue(self):
        return self._max_priority

    def getTotalCount(self) -> int:
        return self._total_count

    def getLength(self) -> int:
        return self._count

    def dequeue(self) -> Tuple[str, int]:
        for i in range(self._max_priority):
            if len(self._level_queue_dict[i]) > 0:
                self._count = self._count - 1
                return (self._level_queue_dict[i].pop(0), i + 1)

        return None

    def enqueue(self, link, priority):
        if self._max_priority < priority:
            for i in range(self._max_priority, priority):
                self._level_queue_dict[i] = []
            self._max_priority = priority

        self._level_queue_dict[priority - 1].append(link)
        self._count = self._count + 1
        self._total_count = self._total_count + 1