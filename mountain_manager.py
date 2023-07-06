from mountain import Mountain
from typing import List
from double_key_table import DoubleKeyTable
from algorithms.mergesort import mergesort


class MountainManager:

    def __init__(self) -> None:
        self.mountains = DoubleKeyTable()
        self.track = set()

    def add_mountain(self, mountain: Mountain) -> None:
        self.mountains[str(mountain.difficulty_level), mountain.name] = mountain
        self.track.add(str(mountain.difficulty_level))

    def remove_mountain(self, mountain: Mountain) -> None:
        del self.mountains[str(mountain.difficulty_level), mountain.name]

    def edit_mountain(self, old_mountain: Mountain, new_mountain: Mountain) -> None:
        del self.mountains[str(old_mountain.difficulty_level), old_mountain.name]
        self.mountains[str(new_mountain.difficulty_level), new_mountain.name] = new_mountain

    def mountains_with_difficulty(self, diff: int) -> List[Mountain]:

        if str(diff) not in self.track:
            return []
        return self.mountains.values(str(diff))

    def group_by_difficulty(self) -> List[List[Mountain]]:
        keep = []
        for key in mergesort(self.mountains.keys()):
            keep.append(self.mountains_with_difficulty(key))
        return keep
