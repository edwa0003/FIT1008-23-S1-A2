from __future__ import annotations

from mountain import Mountain
from algorithms.mergesort import mergesort

class MountainOrganiser:

    def __init__(self) -> None:
        self.mountain_organizer=[]

    def cur_position(self, mountain: Mountain) -> int: #worst case complexity O(N). N being the len of self.mountain_organizer, which means the mountain is at the end or the mountain is not found
        for i in range(len(self.mountain_organizer)): #best case O(1).when the mountain is at index 0.
            if self.mountain_organizer[i]==mountain:
                return i
        raise KeyError(mountain)

    def add_mountains(self, mountains: list[Mountain]) -> None: #worst case complexity O(N^2). N being how many items in mountains, best O(1) meaning only 1 item in mountains.
        for mountain in mountains:
            self.mountain_organizer.append(mountain)
        list_to_sort=[]
        for mountain in self.mountain_organizer:
            list_to_sort.append((mountain.length,mountain.name)) #making it to a tuple so can be sorted by mergesort
        sorted_tuple_list=mergesort(list_to_sort)

        new_mo=[] #a sorted list of mountains
        for i in sorted_tuple_list:
            for j in self.mountain_organizer:
                if i[1] == j.name:
                    new_mo.append(j)
        self.mountain_organizer=new_mo
        return None



