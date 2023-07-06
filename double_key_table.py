from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241,
                   786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        """Follow a path and add mountains according to a personality.
        Args:
        - sizes which is a list, if it's none use TABLE_SIZES as sizes
        - internal sizes which is a list, if it's none use TABLE_SIZES as internal sizes

        Raises: None

        Returns: None, but initializes double key table

        Complexity:
        - Worst case: O(comp+comp+list.get_item)
        - Best case: the same
        """
        self.sizes = sizes
        if self.sizes is None:
            self.sizes = self.TABLE_SIZES
        self.internal_sizes = internal_sizes
        if self.internal_sizes is None:
            self.internal_sizes = self.TABLE_SIZES
        self.size_index = 0
        self.table = ArrayR(self.sizes[self.size_index])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.
        Args:
        - key1 which is a generic type object
        - key2 which is a generic type object
        - is_insert which is a bool. If we are inserting an item, is_insert is True. If we are getting an item, is_insert is False.

        Raises:
        - raises KeyError: When the key pair is not in the table, but is_insert is False.
        - raises FullError: When a table is full and cannot be inserted.

        Returns:
        - A tuple containing the position of the objects. The first integer is the location in the top level table. The second integer is the lacation in
        the inner bottom level table.

        Complexity:
        - Worst case: When is_insert is False. O(hash1+N*(ArrayR.get_item+comp)+ArrayR.get_item+LinearProbeTable._linear_probe)= O(N*(ArrayR.get_item+comp)).
        N being how many items in that clusters. This happens when the top level key exists and is at the end of the cluster, but the bottom level key doesn't exist.
        We have to go through the entire cluster at the top level table. Then we have to go through the entire cluster again at the bottom level.
        - best case: When is_insert is False. O(hash1+ArrayR.get_item+comp+ArrayR.get_item+LinearProbeTable._linear_probe). Meaning when we hash key1 we immediately get the
        key we want. Then we hash key2, again we immediately get the key we want.
        """
        # Initial position
        pos1 = self.hash1(key1)

        for _ in range(self.table_size):
            if self.table[pos1] is None:
                # Empty spot. Am I upserting or retrieving?
                if is_insert:  # this means key1 has no value and we can key2 wherever we want
                    sample_inner_dict = LinearProbeTable(self.internal_sizes)
                    pos2 = self.hash2(key2, sample_inner_dict)
                    return (pos1, pos2)
                else:
                    raise KeyError(key1)
            elif self.table[pos1][0] == key1:  # this means we have found key1
                inner_dict = self.table[pos1][1]  # getting the value of key1
                pos2 = inner_dict._linear_probe(key2,is_insert)  # linear probing through the value of key1 which is a dictionary
                return (pos1, pos2)
            else:
                # Taken by something else. Time to linear probe.
                pos1 = (pos1 + 1) % self.table_size

        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError(key1)

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for entry in self.table:
                if entry is not None:
                    yield entry[0]
        else:
            pos1 = self.hash1(key)
            if self.table[pos1] is not None:
                inner_dict = self.table[pos1][1]
                for k2 in inner_dict.keys():
                    yield k2

    def keys(self, key: K1 | None = None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        Args:
        - key, which is a generic type object.

        Returns:
        - A list containing either all the top-level keys in the table if key is None.
        Or returns all bottom-level keys for the corresponding top-level key.

        Complexity:
        - Worst: O(comp+N*(comp+comp+LinearProbeTable.keys))=O(N*(comp+comp=LinearProbeTable.keys)), N being the table size.
        This happens when the top level key doesn't exist. So we need to iterate through the whole top level table.
        - Best: O(1+LinearProbeTable.keys). Meaning the top level key we entered is in index 0 of the top level table.
        """
        if key:
            for inner_array in self.table: #searching for the key
                if inner_array is not None:
                    if inner_array[0]==key:
                        inner_dict=inner_array[1]
                        return inner_dict.keys() #using keys method from linear probe table
        else:
            keys_array = []
            for inner_array in self.table:  # looping through the table
                if inner_array is not None:
                    key1, inner_dict = inner_array
                    keys_array.append(key1)  # appending to keys array
            return keys_array


    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            for entry in self.table:
                if entry is not None:
                    inner_dict = entry[1]
                    for value in inner_dict.values():
                        yield value
        else:
            pos1 = self.hash1(key)
            if self.table[pos1] is not None:
                inner_dict = self.table[pos1][1]
                for k2, value in inner_dict.items():
                    if k2 == key or (isinstance(k2, tuple) and k2[0] == key):
                        yield value

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        Args:
        - key, which is a generic type object.

        Returns:
        - A list containing either all the values in the table if key is None.
        Or returns all the values for the corresponding top-level key.

        Complexity:
        - Worst: O(comp+N*(comp+comp+LinearProbeTable.values))=O(N*(comp+comp+LinearProbeTable.keys)). N being the table size.
        This happens when the top level key doesn't exist. So we need to iterate through the whole top level table.
        - Best: O(1+LinearProbeTable.values). Meaning the top level key we entered is in index 0 of the top level table.
        """
        if key is None:
            values_list=[]
            for inner_array in self.table:
                if inner_array is not None:
                    inner_dict=inner_array[1]
                    inner_dict_values=inner_dict.values()
                    for value in inner_dict_values:
                        values_list.append(value)
            return values_list
        else:
            for inner_array in self.table: #searching for the key
                if inner_array is not None:
                    if inner_array[0]==key:
                        inner_dict=inner_array[1]
                        return inner_dict.values() #using values method from linear probe table

    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        Args:
        - key, which is a generic type object.

        Returns:
        - The value for those keys

        Complexity:
        - Worst: O(_linear_probe). This means that the item doesn't exist. So we need to iterate through the whole cluster.
        - Best: O(_linear_probe). This means that we hash and straight away get the item at that position.
        """
        key1, key2 = key
        pos1,pos2=self._linear_probe(key1,key2,False)
        inner_dict = self.table[pos1][1]
        data=inner_dict[key2]
        return data

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        key1, key2 = key
        pos1, pos2 = self._linear_probe(key1, key2, True)

        if self.table[pos1] is None:  # key1 is not in table hence has no value
            inner_array = ArrayR(2)  # creating [none,none]
            inner_dict = LinearProbeTable(self.internal_sizes)  # creating empty inner dictionary
            inner_dict.hash = lambda k: self.hash2(k, inner_dict)  # setting the hash for the inner dictionary
            inner_dict[key2] = data  # setting the inner dictionary
            inner_array[0] = key1  # creating [key1,none]
            inner_array[1] = inner_dict  # creating [key1,inner dictionary]
            self.table[pos1] = inner_array  # inserting [key1,inner dictionary] to the outer table in position 1
        else:  # if there is already something in pos1, key1 is in table and has a value
            inner_dict = self.table[pos1][1]  # getting the inner dictionary which has been filled
            inner_dict[key2] = data  # setting the inner dict
            self.table[pos1][1] = inner_dict  # inserting back the new modified inner dict
        self.count += 1
        if self.count >= self.sizes[self.size_index]:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        # biasanya key1 tetap ada tapi key2 dihapus
        # kalau len dari value key1 hanya 1 berarti hapus key1 dan key2
        key1, key2 = key

        if len(key) == 1:
            # Removing a key-value pair from inner dictionary
            for outer_pos in range(self.table_size):
                if self.table[outer_pos] is not None and self.table[outer_pos][1].__contains__(key1):
                    # We found the key1, now let's remove key2 from its inner dictionary
                    del self.table[outer_pos][1][key1][key2]
                    if len(self.table[outer_pos][1][key1]) == 0:
                        # If there are no more key-value pairs in the inner dictionary, delete the outer key-value pair
                        del self.table[outer_pos][1][key1]
                        if len(self.table[outer_pos][1]) == 0:
                            self.table[
                                outer_pos] = None  # If there are no more key-value pairs in the outer dictionary, delete the entire inner dictionary
                    self.count -= 1
                    return
            # If the outer loop completes without finding the key, raise a KeyError
            raise KeyError(key1)

        elif len(key) == 2:
            # Removing a key-value pair from outer dictionary
            pos1 = self.hash1(key1)
            for _ in range(self.table_size):
                if self.table[pos1] is None:
                    raise KeyError(key1)
                elif self.table[pos1][0] == key1:
                    # We found the key1, now let's remove the entire inner dictionary associated with key1
                    del self.table[pos1][1][key2]
                    if len(self.table[pos1][1]) == 0:
                        # If there are no more key-value pairs in the inner dictionary, delete the outer key-value pair
                        self.table[pos1] = None
                    self.count -= 1
                    return
                else:
                    # Taken by something else. Time to linear probe.
                    pos1 = (pos1 + 1) % self.table_size
            # If the loop completes without finding the key, raise a KeyError
            raise KeyError(key1)

        else:
            raise KeyError("Invalid key")

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.table
        self.size_index += 1
        if self.size_index == len(self.sizes):
            return
        self.table = ArrayR(self.sizes[self.size_index])

        self.count = 0
        for item in old_array:
            if item is not None:
                key1, inner_table = item
                keys = self.keys(key1)
                for i in inner_table.array:
                    if i is not None:
                        k, v = i
                pos1, _ = self._linear_probe(key1, k, True)
                self.table[pos1] = item

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.table)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()