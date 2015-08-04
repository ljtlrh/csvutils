import csv, random


class csvrdwt(object):


    def __init__(self, f, new=False ):

        self.f = f
        self.containter = []
        self.sorted = False
        self.sorted_copy = None
        self.fieldnames = None

        if not new:
            try:
                with open(f, 'r') as file:
                    reader = csv.DictReader(file)

                    self.fieldnames = reader.fieldnames

                    for row in reader:

                        self.containter.append({ key : row[key] for key in self.fieldnames })

            except Exception as e:
                raise e


    def _input_check(self, input):
        '''
        Checks for a valid input dictionary
        '''

        if not isinstance(input, dict):
            raise TypeError('Row input must be of type dictionary')

        for key in self.fieldnames:
            if not key in input.keys():
                raise KeyError('Row must include all defined fieldnames')

        for key in input.keys():
            if not key in self.fieldnames:
                raise KeyError('Invalid fieldnames provided')

        return True

    def write_headers(self, input):

        if isinstance(input, list):
            self.fieldnames = input
        else:
            raise TypeError('fieldnames must be of type list')


    def write_row(self, input):
        '''
        input - dictionary, keys of dictionary must match the fields of the csv
        '''
        self._input_check(input)

        # Check for duplicates, not optimized
        for row in self.containter:
            match = True

            for key in self.fieldnames:
                if row[key] != input[key]:
                    match = False
                    break

            if match == True:
                return

        self.containter.append(input)
        self.sorted = False

    def remove_row(self, input):
        '''
        input - dictionary, keys of dictionary must match the fields of the csv
        '''
        #self._input_check(input)

        # Sort data to help reduce search time
        self._input_check(input)

        if not self.sorted:
            self._sort()

        match ,value = self._bsearch(self.sorted_copy, input, self.fieldnames[0])

        if match:
            self.containter.remove(value)


    def _sort(self):

        self.sorted_copy = sorted(self.containter,key=lambda k: k[self.fieldnames[0]])
        self.sorted = True


    def _bsearch(self,seq, input, key):

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
                for row in self.containter:
                    writer.writerow(row)

        except Exception as e:
            raise e


    def __str__(self):

        output = ''

        for i,col in enumerate(self.fieldnames):
            if i < len(self.fieldnames)-1:
                output += '{},'.format(col)
            else:
                output += '{}'.format(col)

        for num,row in enumerate(self.containter):
            output+='\n'

            for i,key in enumerate(self.fieldnames):
                if i < len(self.fieldnames)-1:
                    output+='{},'.format(row[key])
                else:
                    output+='{}'.format(row[key])

        return output


if __name__ == '__main__':

    a = csvrdwt('names.csv')

    a.write_row({'first': 'brian', 'middle': 't', 'last':'yun'})

    a.save()

    a.write_row({'first': 'Jeremy', 'middle': 't', 'last':'sexton'})

    a.save()

    a.write_row({'first': 'george', 'middle':'y', 'last':'field'})

    a.save()

    a.remove_row({'first': 'Jeremy', 'middle': 't', 'last':'sexton'})
    a.remove_row({'first': 'brian', 'middle': 't', 'last':'yun'})

    print(a)

    a.save()