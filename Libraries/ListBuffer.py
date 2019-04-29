class ListBuffer(list):
    """
    A class which acts like a collections deque (has a maximum length) but with the functionality of a list.
    The tradeoff is performance, and this is only viable for smallish objects.
    That said, as the length of appended elements increases, performance differences become smaller.
    """
    def __init__(self, iterable, maxlen=None):
        super().__init__(iterable)
        if maxlen is not None:
            self.maxlen = maxlen
        else:
            self.maxlen = len(iterable)
        delta = self.maxlen - len(self)
        self[-delta:] = []

    @property
    def maxlen(self):
        return self._maxlen

    @maxlen.setter
    def maxlen(self, value):
        """
        Allows updating of the maxlen property. Also updates the main objects len to match the new maxlen.
        :param value: maximum length of the buffer list.
        :type value: int
        :return: None
        """
        assert isinstance(value, int), "maxlen must be a positive integer!"
        assert value >= 0, "maxlen must be a positive integer!"
        self._maxlen = value
        delta = self.maxlen - len(self)
        self[-delta:] = []

    def add(self, element):
        """
        Unlike a lists' extend or append methods, this method accepts single elements or an iterable.
        :param element: list or single element
        :type element: Union[list, float, int]
        :return: None
        """
        try:
            data_len = len(element)
            new_len = data_len + len(self)
            delta = self.maxlen - new_len
            if len(self) == self.maxlen and 1 < delta < self.maxlen:
                self[:-data_len] = self[data_len:]
                self[-data_len:] = element
            else:
                self.extend(element)
                if delta < 0:
                    self[:-delta] = []

        except TypeError:       # if item is not iterable
            # since we're using lists here, there are not type errors and such.
            # we can allow appending of a list in a list of floats or whatever the user wants to do!
            self.append(element)
            if len(self) > self.maxlen:
                self.__delitem__(0)
