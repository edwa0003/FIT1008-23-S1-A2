from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

from data_structures.linked_stack import LinkedStack
# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       ___path_top____
      /               \
    -<                 >-path_follow-
      \__path_bottom__/
    """

    path_top: Trail
    path_bottom: Trail
    path_follow: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.path_follow.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """Removes the mountain at the beginning of this series."""
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        return TrailSeries(mountain,Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        return TrailSplit(Trail(),Trail(),Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        new_following = self.following.add_mountain_before(mountain)
        return TrailSeries(self.mountain,new_following)

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
        new_following = self.following.add_empty_branch_before()
        return TrailSeries(self.mountain,new_following)

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """Adds a mountain before everything currently in the trail."""
        new_store=TrailSeries(mountain, Trail(self.store))
        return Trail(new_store)

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        new_store=TrailSplit(Trail(),Trail(),Trail(self.store) )
        return Trail(new_store)

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality.
        Args:
        - personality: which is an object of WalkerPersonality

        Raises: None

        Returns: None, but adds mountains to the personality

        Complexity:
        - Worst case: O(n*(isinstance+add_mountain+comp+linked_stack.pop)+(isinstance+linked_stack.push+WalkerPersonality.select_branch+comp)+(linked_stack.pop) ) ), where n is how many trails there are
        - Best case: O(isinstance+isinstance+linked_stack.is_empty() ), which means the whole trail is None and we stop the loop.
        """
        current_path = self.store
        TrailSplit_stack=LinkedStack()#this is a list filled with TrailSplit
        while True:
            if isinstance(current_path,TrailSeries):
                personality.add_mountain(current_path.mountain)
                current_path=current_path.following.store #moving to the following trail of the TrailSeries
                if current_path is None: #checking if the following trail is none, to see if there could be a following trail in TrailSplit
                    if TrailSplit_stack.is_empty():
                        return None
                    else:#if the current_path is part of a TrailSplit then change the path to the path_follow of that TrailSplit
                        current_path=TrailSplit_stack.pop() #changing the current_path to the path_follow of that TrailSplit
                        current_path=current_path.path_follow.store
            elif isinstance(current_path,TrailSplit):
                TrailSplit_stack.push(current_path)#adding this TrailSplit just in case we need to backtrack
                if personality.select_branch(current_path.path_top,current_path.path_bottom) is True:
                    current_path=current_path.path_top.store
                else:
                    current_path=current_path.path_bottom.store
            else:#if current_path is not TrailSplit or TrailSeries, then it is None
                if TrailSplit_stack.is_empty():
                    return None
                current_path=TrailSplit_stack.pop()
                current_path=current_path.path_follow.store #it goes to one of the branches of a TrailSplit and then it goes to of the none branches, then it backtracks and goes to the path_follow of that TrailSplit

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        res=[]
        if isinstance(self.store,TrailSplit):
            res += self.store.path_top.collect_all_mountains()
            res += self.store.path_bottom.collect_all_mountains()
            res += self.store.path_follow.collect_all_mountains()
        elif isinstance(self.store,TrailSeries):
            if self.store.mountain not in res:
                res += [self.store.mountain]+self.store.following.collect_all_mountains()
        return res

    def length_k_paths(self, k) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        all_paths_list = []
        start_path_mountains = []
        trail_split_stack = []
        self.length_k_paths_aux(self.store, start_path_mountains, all_paths_list, trail_split_stack)
        return [path for path in all_paths_list if len(path) == k]

    def length_k_paths_aux(self, current_path: TrailStore, current_path_mountains: list[Mountain],all_paths_list: list[list[Mountain]], trail_split_stack):

        if current_path is None:
            if not trail_split_stack:
                all_paths_list.append(current_path_mountains)
            else:
                following = trail_split_stack.pop()
                self.length_k_paths_aux(following, current_path_mountains, all_paths_list, trail_split_stack)

        elif isinstance(current_path, TrailSeries):
            current_path_mountains.append(current_path.mountain)
            self.length_k_paths_aux(current_path.following.store, current_path_mountains, all_paths_list,trail_split_stack)

        elif isinstance(current_path, TrailSplit):
            parent_trail_split = trail_split_stack[-1] if trail_split_stack else None
            trail_split_stack.append(current_path.path_follow.store)
            top_path_list = current_path_mountains.copy()
            self.length_k_paths_aux(current_path.path_top.store, top_path_list, all_paths_list, trail_split_stack)

            trail_split_stack.append(parent_trail_split)
            trail_split_stack.append(current_path.path_follow.store)
            bottom_path_list = current_path_mountains.copy()
            self.length_k_paths_aux(current_path.path_bottom.store, bottom_path_list, all_paths_list, trail_split_stack)