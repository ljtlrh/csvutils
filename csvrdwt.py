import csv


class Csvrdwt(object):
    """"
    Csv class for reading and writing to file.
    """"
    def __init__(self, f, new=False):

        self.f = f
        self.container = []
        self.sorted = False
        self.sorted_copy = []
        self.fieldnames = None
        self.sort_criteria = 0
        self.sort_reversed = False

        if not new:
            try:
                with open(f, 'r') as file:
                    reader = csv.DictReader(file)

                    self.fieldnames = reader.fieldnames

                    for row in reader:

                        self.container.append({key: row[key] for key in self.fieldnames})

            except Exception as e:
                raise e

    def _input_check(self, input):
        """
        Checks for a valid input dictionary
        input:: dictionary
        """

        if not isinstance(input, dict):
            raise TypeError('Row input must be of type dictionary')

        for key in self.fieldnames:
            if not key in input.keys():
                raise KeyError('Row must include all defined fieldnames')

        for key in input.keys():
            if not key in self.fieldnames:
                raise KeyError('Invalid fieldnames provided')

        return True

    def _headers_check(self, input):
        """
        Checks if the values in input are valid fieldnames
        """

        return all([ i in self.fieldnames for i in input])

    def write_headers(self, *input):
        """
        Write fieldname headers.

        input:: list of strings
        """

        if isinstance(input, tuple):
            if not self.fieldnames is None and len(self.fieldnames) != len(input):
                raise ValueError('Cannot overwrite file fieldnames with an unequal amount of new fieldnames')

            self.fieldnames = list(input)
        else:
            raise TypeError('fieldnames must be of type tuple')

        return

    def write_row(self, input):
        """
        input - dictionary, keys of dictionary must match the fields of the csv
        """
        self._input_check(input)

        # Check for duplicates, not optimized
        for row in self.container:
            match = True

            for key in self.fieldnames:
                if row[key] != input[key]:
                    match = False
                    break

            if match:
                return

        self.container.append(input)
        self.sorted = False

        return

    def make_list(self, *values, sort=False):
        """
        Returns a custom list based upon the value(s) supplied
        """


        if not self._headers_check(values):
            raise ValueError('Unable to make list with unknown fieldnames.')

        result = list()

        if sort:
            if not self.sorted:
                self._sort(reverse=self.sort_reversed)

            for row in self.sorted_copy:
                if len(values) == 1:
                    result.append(row[values[0]])
                else:
                    result.append(tuple([row[x] for x in values]))

            return result

        for row in self.container:
            if len(values) == 1:
                result.append(row[values[0]])
            else:
                result.append(tuple([row[x] for x in values]))

        return result

    def make_dict(self, key, *values):
        """
        Returns a custom dictionary based on the key and value(s) supplied
        """

        if not self._headers_check(values+(key,)):
            raise ValueError('Unable to make list with unknown fieldnames.')

        result = dict()

        for row in self.container:
            if len(values) == 1:

                # Check if there already exists an entry for the key value, if False create a new key value
                if result.get(row[key], False):

                    # Check if value is already a tuple, if so added to that tuple, if not change value from string to tuple
                    if isinstance(result.get(row[key]),tuple):
                        result[row[key]] += (row[values[0]],)
                    else:
                        result[row[key]] = (result[row[key]],) + (row[values[0]],)
                else:
                    result[row[key]] = row[values[0]]
            else:
                if result.get(row[key], False):

                    if isinstance(result.get(row[key]), list):
                        result[row[key]].appdned(tuple([row[x] for x in values]))
                    else:
                        result[row[key]] = [result[row[key]]] + [tuple([row[x] for x in values])]

                else:
                    result[row[key]] = tuple([row[x] for x in values])

        return result

    def remove_row(self, input):
        '''
        input - dictionary, keys of dictionary must match the fields of the csv
        '''

        # Sort data to help reduce search time
        self._input_check(input)

        if not self.sorted:
            self._sort(reverse=self.sort_reversed)

        match ,value = self._bsearch(self.sorted_copy, input, self.fieldnames[self.sort_criteria])

        if match:
            self.container.remove(value)
            self.sorted_copy.remove(value)

        return

    def _sort(self, reverse=False):
        """
        Creates a sorted copy of the data container
        """

        self.sorted_copy = sorted(self.container,reverse=reverse,key=lambda k: k[self.fieldnames[self.sort_criteria]])
        self.sorted = True

        return


    def _bsearch(self,seq, input, key):
        """
        Binary seach implementation
        seq = dictionary to search
        input = dictionary
        key = what key value to search for

        """

        start = 0
        end = len(seq)

        while start < end:

            select = (start+end) // 2

            if seq[select][key] == input[key]:

                if all([input[k] == seq[select][k] for k in self.fieldnames]):
                    return True, seq[select]

            if seq[select][key] < input[key]:
                start = select + 1

            else:
                end = select

        return False, None

    def save(self, f=None):
        '''
        Saves csv object in memory to file
        '''
        if f is None:
            f =self.f

        try:
            with open(f, 'w') as csvfile:

                writer = csv.DictWriter(csvfile,fieldnames=self.fieldnames)
                writer.writeheader()
                for row in self.container:
                    writer.writerow(row)

        except Exception as e:
            raise e

        return

    def sort_by(self, column=0, reverse=False):
        """
        Sets what header to sort by and selects ascending or decending
        """

        if 0 <= column < len(self.fieldnames):
            self.sort_criteria = column
            self.sort_reversed = reverse

        return

    def sort(self):
        """
        Sorts the data container not just the copy
        """

        self.container = sorted(self.container,reverse=self.sort_reversed,key=lambda k: k[self.fieldnames[self.sort_criteria]])
        self.sorted_copy = self.container[::]
        self.sorted = True

        return

    def __len__(self):

        return len(self.container)

    def __getitem__(self, k):

        if k < 0:

            k += len(self)

        if not 0 <= k < len(self):
            raise IndexError('index out of range')

        return self.container[k]

    def __str__(self):

        output = ''

        for i,col in enumerate(self.fieldnames):
            if i < len(self.fieldnames)-1:
                output += '{},'.format(col)
            else:
                output += '{}'.format(col)

        for num,row in enumerate(self.container):
            output+='\n'

            for i,key in enumerate(self.fieldnames):
                if i < len(self.fieldnames)-1:
                    output+='{},'.format(row[key])
                else:
                    output+='{}'.format(row[key])

        return output


if __name__ == '__main__':

    a = Csvrdwt('hostnames.txt')



    a.sort_by(1)

    print(a.container)
    print(a.sorted_copy)

    a.remove_row({'clli': 'bftnsc54', 'abbreviation': 'blf', 'hub_code': '4S', 'city': 'bluffton'})


    r = dict()

    for row in a:
        r[row['city']+' - '+row['clli']] = row['hub_code']

    print(a.container)
    print(a.sorted_copy)
