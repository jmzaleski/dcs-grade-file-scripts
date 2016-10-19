import re
from Namespace import Namespace

class GradeFileReaderWriter(object):
    """read a Jim Clarke style grades file and squirrel away the data for later.
    Later we will use this object to retreive lines that match a given query and
    append a new mark to the lines, and finally write them to a new grades file
    """

    def __init__(self, fn):
        self.grade_file_name = fn
        self.line_array = []
        self.line_value_index = {}
        #list of marks in order they were found in the grade file
        self.mark_names = ["student_no"]
        self.mark_definitions = {"student_no":None}
        self.field_number_of_mark_definition = {}
        self.separator = None #maybe should say tab or whatever default is in grade file
        self.students = []
        self.read_file()
        return

    def read_file(self):
        """
         reads the lines out of the grades file, including the header.
         See http://www.cdf.toronto.edu/~clarke/grade/fileformat.shtml
        :return:
        """
        try:
            #open read binary so as to not mess up the line endings and whatnot
            with open(self.grade_file_name, 'rb') as grade_file:
                grade_file = open(self.grade_file_name, 'rb')
                #first three chars of file may set separator character for marks
                first_line = grade_file.readline().decode('UTF-8')
                self.line_array.append(first_line)

                if first_line.startswith("*/"):
                    assert len(first_line)>3
                    self.separator = first_line[2]
                    print("found separator", self.separator)

                # scan lines in file header looking for mark defintions
                ix_mark_defn = 0
                ix_line_number = 1
                for bline in grade_file: # examine header of file
                    line = bline.decode('UTF-8').rstrip('\n')
                    if len(line) == 0:
                        break #empty line ends header
                        self.line_array.append(line)
                        #self.line_value_index[line] = ix  # remember the spot in line_array..
                    ix_line_number += 1
                    vals = line.split()
                    if vals[0].startswith("*"):
                        continue # comments not interesting
                    #eg: a1 / 10
                    mark_defn_name = vals[0]
                    self.mark_names.append(mark_defn_name)
                    mark_decl = vals[1:]
                    self.mark_definitions[mark_defn_name] = mark_decl
                    self.field_number_of_mark_definition[mark_defn_name] = ix_mark_defn
                    ix_mark_defn += 1

                print(self.mark_names)
                print(self.mark_definitions)
                print(self.field_number_of_mark_definition)

                #squirrel away rest of file
                for bline in grade_file:
                    line = bline.decode('UTF-8').rstrip('\n')
                    assert len(line) != 0
                    self.line_array.append(line)
                    self.line_value_index[line] = ix_line_number  # remember the spot in line_array..
                    vals = line.split(self.separator)
                    ns = Namespace().init_names(self.mark_names)
                    ix = 0
                    #TODO: how would a cool kid do this?
                    for name in self.mark_names:
                        if ix < len(vals):
                            ns.set(name,vals[ix])
                        ix +=1
                    self.students.append(ns)
                    ix_line_number += 1

                grade_file.close()
                return self
        except:
            raise Exception("GradeFileReader fails to read " + self.grade_file_name)

        return self


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

if __name__ == '__main__':
    gfr = GradeFileReaderWriter("/tmp/CSC300H1F-empty").read_file()
    #list comprehensions considered powerful!
    for ta in set([ns.ta for ns in gfr.students]):
        print(ta,[ns.utorid for ns in gfr.students if ns.ta == ta])



