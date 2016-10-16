
class GradeFileReaderWriter(object):
    """read a Jim Clarke style grades file and squirrel away the data for later.
    Later we will use this object to retreive lines that match a given query and
    append a new mark to the lines, and finally write them to a new grades file
    """
    import re
    def __init__(self, fn):
        self.grade_file_name = fn
        self.line_array = []
        self.line_value_index = {}
        self.read_file()
        return

    def read_file(self):
        """
         reads the lines out of the grades file, including the header.
        :return:
        """
        try:
            with open(self.grade_file_name, 'rb') as grade_file:
                grade_file = open(self.grade_file_name, 'rb')
                ix = 0
                for bline in grade_file:
                    line = bline.decode('UTF-8').rstrip('\n')
                    self.line_array.append(line)
                    self.line_value_index[line] = ix  # remember the spot in line_array..
                    ix += 1
                grade_file.close()
        except:
            raise Exception("GradeFileReader fails to read " + self.grade_file_name)

    def matching_lines(self, query):
        "return lines that match the query"
        return [l for l in self.line_array if re.search(query,l)]

    def append_mark_to_line(self,student_line,mark):
        """append the mark, which may be a string or a number, to the right line.
        Returns true if line is found and mark appended correctly, o/w False"""
        if student_line in self.line_value_index:
            ix = self.line_value_index[student_line]
            before = self.line_array[ix]
            after = before
            if not after.endswith(","):
                after += ","
            after += str(mark)
            self.line_array[ix] = after
            print("line[", ix, "] <-", after)
            return True
        else:
            #print(student_line, "not in", self.line_value_index)
            return False

    def print(self):
        """debugging.. print the arrays"""
        print("GradeFileReader.line_array", self.line_array)
        print("GradeFileReader.line_value_array", self.line_value_index)

    def write_to_new_grade_file(self,fn):
        """write the modified lines out to a new file name"""
        with open(fn,'w') as new_file:
            for l in self.line_array:
                print(l, file=new_file)