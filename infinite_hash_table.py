from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR
from data_structures.linked_stack import LinkedStack
K = TypeVar("K")
V = TypeVar("V")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self) -> None:
        self.level=0
        self.table=ArrayR(self.TABLE_SIZE)
        self.count=0

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        sequence=self.get_location(key)
        current_table = self.table
        for pos in sequence:
            if current_table[pos][0]==key:
                return current_table[pos][1]
            current_table=current_table[pos][1]

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        pos = self.hash(key)
        current_table = self.table
        while True:
            if current_table[pos] is None: #if there is nothing at that position
                array=ArrayR(2) #put the key value pair as array, not tuple. because we might need to change its value to a table and move that value to a deeper position.
                array[0]=key
                array[1]=value
                current_table[pos]=array #means we can put our key value pair in that position
                self.count += 1 #adding to count
                self.level=0
                return None
            elif isinstance(current_table[pos][1], ArrayR):
                current_table = current_table[pos][1] #going deeper
                self.level += 1
                pos = self.hash(key)
            elif current_table[pos][0]==key: #we put this here because there is chance to get to the actual key we would need go deeper by one level
                current_table[pos][1]=value #updating key
                return None
            else:#this means there is a conflict and we need to go deeper. But we can't because the value there is not an array.
                old_key=current_table[pos][0] #getting the current key
                old_value=current_table[pos][1] #getting the current value
                current_table[pos][0]=current_table[pos][0][0:self.level+1] #modifying the current key, i.e when we enter leg they key at level 0 changes from lin to l
                current_table[pos][1]=ArrayR(self.TABLE_SIZE) #changing the value of the current key to an array
                self.level+=1 #adding level because we are going to hash at a deeper level
                key_to_hash=old_key[0:self.level+2]
                key_to_hash_pos=self.hash(key_to_hash) #finding the position to put the modified key
                if self.hash(old_key)==key_to_hash_pos:
                    key_to_hash=old_key
                array=ArrayR(2) #creating an empty array
                array[0]=key_to_hash #inserting the key that we have hashed
                array[1]=old_value #inserting the current value
                current_table[pos][1][key_to_hash_pos]=array #putting the array which is a key value pair that we just created at the empty hash table we created
                self.level-=1 #decrementing the level since we have finished the process


    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        key_location = self.get_location(key)
        current_depth = 0
        current_table = self.table
        stack = LinkedStack()
        stack.push(current_table)

        # Traverse the tables until the second to last index in key_location
        while current_depth < len(key_location) - 1:
            current_table = current_table[key_location[current_depth]][1]
            stack.push(current_table)
            current_depth += 1

        # Remove the item at the final location
        current_depth = len(key_location) - 1
        current_table[key_location[current_depth]] = None
        self.count -= 1
        found_item = False
        item_to_move = None

        # Traverse the stack of tables and restructure them as needed
        while not stack.is_empty():
            current_table = stack.pop()
            non_none_count = 0

            # Count the number of non-None elements in the table
            for index in range(len(current_table)):
                if current_table[index] is not None:
                    non_none_count += 1
                    last_non_none_index = index

            # If the table has only one element and we are not at the root level
            if non_none_count == 1 and current_depth > 0:

                # If we have not yet found an item to move up the tree
                if found_item == False and not isinstance(current_table[last_non_none_index][1], ArrayR):

                    # Traverse the table and find the first non-None element
                    for index in range(len(current_table)):
                        if current_table[index] is not None:
                            item_to_move = current_table[index]
                            found_item = True
                            current_table[index] = None
                            current_depth -= 1

                # If we have already found an item to move up the tree
                elif found_item == True:
                    current_table[key_location[current_depth]] = None
                    current_depth -= 1

                # If we have not found an item and there are no more elements to traverse
                else:
                    break

            # If we have an item to move up the tree
            elif item_to_move is not None:
                item_to_move_array=ArrayR(2)
                item_to_move_array[0]=item_to_move[0]
                item_to_move_array[1]=item_to_move[1]
                current_table[key_location[current_depth]] = item_to_move_array

            # If we have no item to move and there are no more elements to traverse
            else:
                break

    def __len__(self): #return how many value in the list
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        return str(print(self.table))

    def get_location(self, key):
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        sequence = []
        current_table = self.table
        pos = self.hash(key)
        while True:
            sequence.append(pos)
            if current_table[pos] is None:  # if it is None in that position that means the key doesn't exist
                raise KeyError(key)
            elif current_table[pos][0] == key:  # this means we may have found the key
                if isinstance(current_table[pos][1],ArrayR): #check if the value of that key is an array
                    check_table=current_table[pos][1]
                    for i in range(self.TABLE_SIZE): #if it is check if the key that we are searching for is in that array
                        if isinstance(check_table[i],ArrayR):
                            if check_table[i][0]==key:
                                sequence.append(i)
                self.level=0
                return sequence
            elif isinstance(current_table[pos][1],ArrayR) is False: #this means there's a collision but we can't go deeper
                raise KeyError(key)
            current_table = current_table[pos][1]  # going into the table of that key
            self.level += 1  # adding level since we're going deeper
            pos = self.hash(key)  # making a new hash position


    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

if __name__ == "__main__":
    ih = InfiniteHashTable()
    ih["lin"] = 1
    ih["leg"] = 2
    ih["mine"] = 3
    ih["linked"] = 4
    ih["limp"] = 5
    ih["mining"] = 6
    ih["jake"] = 7
    ih["linger"] = 8
    print(ih)
    ih['lin']='ashiaap'
    print(ih)