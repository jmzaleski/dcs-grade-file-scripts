from __future__ import print_function  #allows print as function

import re
from Namespace import Namespace

class GradeFileReaderWriter(object):
    """read a Jim Clarke style grades file and squirrel away the data for later.
    See http://www.cdf.toronto.edu/~clarke/grade/fileformat.shtml
    Later we will use this object to retreive lines that match a given query and
    append a new mark to the lines, and finally write them to a new grades file
    """

    def __init__(self, fn):
        self.grade_file_name = fn
        self.line_array = []       #array of data lines in grade file
        self.line_value_index = {} #dict keyed by text of line telling index of line in line_array
        #list of marks in order they were found in the grade file
        self.mark_names = ["student_no"]
        self.mark_definitions = {"student_no":None}
        self.field_number_of_mark_definition = {}
        self.separator = None #maybe should say tab or whatever default is in grade file
        self.students = []
        return

    def get_student_for_unique_utorid(self,utorid):
        "return student with utorid or None"
        #paranoidly checks over and over that utorid's are unique. perhaps should make the table and be done
        the_unique_ns = None
        for ns in self.students:
            if ns.utorid == utorid: #TODO: change this to a predicate lambda
                assert the_unique_ns == None
                the_unique_ns = ns
        return the_unique_ns

    def student_unique_predicate(self,ns,utorid):
        "return student with utorid or None"
        #paranoidly checks over and over that utorid's are unique. perhaps should make the table and be done
        if ns.utorid == utorid: #TODO: change this to a predicate lambda
            return ns

    def student_generator(self, predicate_lambda):
        return (ns for ns in self.students if predicate_lambda(ns))

    def read_file(self):
        """
         reads the lines out of the grades file, including the header.

        :return:
        """
        try:
            #open read binary so as to not mess up the line endings and whatnot
            with open(self.grade_file_name, 'rb') as grade_file:
                grade_file = open(self.grade_file_name, 'rb')
                #first three chars of file may set separator character for marks
                first_line = grade_file.readline().decode('UTF-8').rstrip('\n')
                self.line_array.append(first_line)

                if first_line.startswith("*/"):
                    assert len(first_line)>2
                    self.separator = first_line[2]
                    #print("found separator", self.separator)

                # scan lines in file header looking for mark defintions
                ix_mark_defn = 0
                ix_line_number = 1
                for bline in grade_file: # examine header of file
                    lline = bline.decode('UTF-8').rstrip('\n')
                    line = str(lline) # TODO: how would cool kid do this?
                    self.line_array.append(line)  # want to record empty line separating header too
                    #self.line_value_index[line] = ix_line_number #don't record header or comment lines position
                    ix_line_number += 1

                    if len(line) == 0:
                        break  # empty line ends header

                    #look for comment char in line
                    ix_star = line.find("*")
                    if ix_star == 0:
                        continue #comment line nothing to do
                    elif ix_star <0:
                        ll = line
                    else:
                        ll = line.split("*")[0]
                        if len(ll.strip()) == 0:
                            continue #nothing to left of *
                    expr = ll.translate({ord(c): None for c in '\t '})
                    assert expr.find("*") < 0 #paranoidly check that comment rejection is right

                    #eg:
                    # a1 / 10
                    # utorid "

                    assert expr.find('*') <0 #no comment without any whitespace (?)

                    #TODO: make mark an object with type?
                    if expr.find('/') >= 0:  # mark defintion
                        mark_defn_name = expr.split('/')[0]
                        mark_decl = expr.split('/')[1]         #out of
                        #TODO: make sure this is a number?
                    elif expr.find('"')>=0: #string data definition
                        mark_defn_name = expr.split('"')[0]
                        mark_decl = '"'
                    elif expr.find("=")>=0: #a formula
                        mark_defn_name = expr.split("=")[0]
                        mark_defn_name = expr.split("=")[1]
                    else:
                        print('syntax error in expr', expr, "on line number", ix_line_number, line)
                        assert False #ohoh expression must either be a mark / nn or a string "
                    #print(mark_defn_name, mark_decl)

                    self.mark_names.append(mark_defn_name)
                    self.mark_definitions[mark_defn_name] = mark_decl
                    self.field_number_of_mark_definition[mark_defn_name] = ix_mark_defn
                    ix_mark_defn += 1

                if False: #verbose
                    print(self.mark_names)
                    print(self.mark_definitions)
                    print(self.field_number_of_mark_definition)

                #squirrel away rest of file. any * before separator makes line a comment (not data)

                check_dups = {}
                for bline in grade_file:
                    line = bline.decode('UTF-8').rstrip('\n')
                    assert len(line) != 0
                    self.line_array.append(line)
                    self.line_value_index[line] = ix_line_number  # remember the spot in line_array..
                    #this is a crazy aspect to grade file. first field actually separated into flag (fields)
                    #and
                    vals = line.split(self.separator)
                    student_no = vals[0] #student number and flags and perhaps name
                    #print(ix_line_number,student_no)
                    if "*" in student_no:
                        if False:
                            print("comment:",ix_line_number,line)
                    else:
                        if student_no in check_dups:
                            print("illegal line because it has same student number as line", check_dups[student_no] )
                            assert False
                        # so first blank following student number is char before drop indicator (ughh)
                        ix_first_blank = student_no.find(" ")
                        ix_drop_indicator = ix_first_blank + 1
                        is_drop = student_no[ix_drop_indicator] == 'd'
                        if is_drop:
                            if False:
                                print("skipping dropout:",student_no)
                        else:
                            check_dups[student_no] = ix_line_number
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
    
    def matching_lines_ignore_case(self, query):
        "return lines that match the query"
        lquery = query.lower()
        return [l for l in self.line_array if re.search(lquery,l.lower())]

    def append_mark_to_line(self,student_line,mark):
        """append the mark, which may be a string or a number, to the right line.
        Returns true if line is found and mark appended correctly, o/w False"""
        if student_line in self.line_value_index:
            ix = self.line_value_index[student_line]
            if ix >= len(self.line_array):
                print ("omg:ix beyond array. something broken in script", ix)
                print(self.line_array)
                return False
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
        """write all lines out to a new file name"""
        with open(fn,'w') as new_file:
            for l in self.line_array:
                print(l, file=new_file)


def check_remark(ns, fetch_mark_lambda, ns_a2r):
    "look for missing marks amongst the remarks"
    if not ns:
        print("predicate: ns is None, exit")
        exit(2)
    if not ns_a2r:
        print("predicate: ns_a1r is None, exit")
        exit(2)
    try:
        mark = fetch_mark_lambda(ns)
        remark = fetch_mark_lambda(ns_a2r)
        #print(ns.ta, ns.utorid, "gave mark=", mark, "remark=", remark)
        if mark != remark:
            if not mark:
                return #not interested if a1 is none or zero
            if float(mark) == 0.0:
                return
            if not remark or float(remark) < float(remark):
                print(ns.ta, "gave mark=", mark, "remark=", remark, "for", ns.utorid)

            # print(ns.a1, ns2.a1)
    except:
        print('exception:', ns, ns_a2r)
        exit(2)

if __name__ == 'xx__main__':
    print("a1r")
    gfr_remark = GradeFileReaderWriter("/tmp/a1r").read_file()
    for ns in GradeFileReaderWriter("/tmp/a1").read_file().students:
        check_remark(ns, lambda ns: ns.a1, gfr_remark.get_student_for_unique_utorid(ns.utorid))

    print("a2r")
    gfr_remark2 = GradeFileReaderWriter("/tmp/a2r").read_file()
    for ns in GradeFileReaderWriter("/tmp/a2").read_file().students:
        check_remark(ns, lambda ns: ns.a2, gfr_remark2.get_student_for_unique_utorid(ns.utorid))


if __name__ == '__main__':
    from zip_assignments_for_ta import zip_assignments_for_ta

    zip_assignments_for_ta(
        gfr=GradeFileReaderWriter("/tmp/CSC300H1F-empty"),
        markus_download_dir="/Users/mzaleski/Dropbox/CSC/300/submit/A4",
        dest_dir = "/tmp/a4")
