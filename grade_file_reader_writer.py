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
                    #print("found separator", self.separator)

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
                    else:
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
                    vals = line.split(self.separator)
                    student_no = vals[0]
                    #print(ix_line_number,student_no)
                    if "*" in student_no:
                        if False:
                            print("comment:",ix_line_number,line)
                    else:
                        if student_no in check_dups:
                            print("illegal line because it has same student number as line", check_dups[student_no] )
                            assert False
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

def zip_assignments_for_ta(gfr, markus_download_dir, dest_dir):
    "find the PDF's for all the students in each TAs section and zip them into a separate zip file for each TA"
    from os.path import isfile, join
    gfr.read_file()
    tas = set([ns.ta for ns in gfr.students])
    files_per_ta = {}
    for ta in tas:
        ta_files = []
        # assert len([ns.utorid for ns in gfr.students if ns.ta == ta]) == len(set([ns.utorid for ns in gfr.students if ns.ta == ta]))
        for utorid in [ns.utorid for ns in gfr.students if ns.ta == ta]:
            rel_path = utorid
            dir = "%s/%s/" % (markus_download_dir, rel_path)
            if not os.path.isdir(dir):
                continue
            for fn in [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]:
                ta_files.append(os.path.join(rel_path, fn))
        files_per_ta[ta] = ta_files

    # for ta in tas:
    #    print(ta, len(files_per_ta[ta]), files_per_ta[ta])

    from shutil import copy

    os.makedirs(dest_dir)
    for ta in tas:
        print(ta, ": ", end='')
        ta_dir = os.path.join(dest_dir, ta)
        assert not os.path.isfile(ta_dir)  # oh no a FILE exists where we want to mkdir
        if not os.path.isdir(ta_dir):
            os.makedirs(ta_dir)
        for fn in files_per_ta[ta]:
            src_path = os.path.join(markus_download_dir, fn)
            print(fn, end='')
            copy(src_path, ta_dir)
        print()
        zip_cmd = "zip -r %s.zip %s" % (ta_dir, ta_dir)
        print(zip_cmd)
        #junk = input("doit?")
        # zip all the files in the ta_dir into ta_dir.zip
        os.system(zip_cmd)
        os.system("ls -ld %s.zip" % ta_dir)

if __name__ == 'xx__main__':
    import os
    from os import system
    from os import listdir

    zip_assignments_for_ta(
        gfr=GradeFileReaderWriter("/tmp/CSC300H1F-empty"),
        markus_download_dir="/Users/mzaleski/Dropbox/CSC/300/submit/A2r",
        dest_dir = "/tmp/a2r")

def check_a1_a1r(ns, ns_a1r):
    if not ns:
        print("predicate: ns is None, exit")
        exit(2)
    if not ns_a1r:
        print("predicate: ns_a1r is None, exit")
        exit(2)
    #print(ns.ta, ns.utorid, "gave a1=", ns.a1, "a1r=", ns_a1r.a1)
    try:
        if not ns.a1 == ns_a1r.a1:
            if not ns.a1:
                return #not interested if a1 is none or zero
            if int(ns.a1) == 0:
                return
            print(ns.ta, "gave a1=", ns.a1, "a1r=", ns_a1r.a1, "for", ns.utorid)
            # print(ns.a1, ns2.a1)
    except:
        print('exception:', ns, ns_a1r)
        exit(2)

def check_a2_a2r(ns, ns_a2r):
    if not ns:
        print("predicate: ns is None, exit")
        exit(2)
    if not ns_a2r:
        print("predicate: ns_a1r is None, exit")
        exit(2)
    #print(ns.ta, ns.utorid, "gave a2=", ns.a2, "a2r=", ns_a2r.a2)
    try:
        if not ns.a2 == ns_a2r.a2:
            if not ns.a2:
                return #not interested if a1 is none or zero
            if float(ns.a2) == 0.0:
                return
            #so a2 got a mark. Did a2r?
            if not ns_a2r.a2 or float(ns_a2r.a2) < float(ns.a2):
                print(ns.ta, "gave a2=", ns.a2, "a2r=", ns_a2r.a2, "for", ns.utorid)

            # print(ns.a1, ns2.a1)
    except:
        print('exception:', ns, ns_a2r)
        exit(2)


def look_for_missing_marks(gfr_a1, gfr_a1r, callback):
    "find the PDF's for all the students in each TAs section and zip them into a separate zip file for each TA"
    from os.path import isfile, join
    gfr_a1.read_file()
    gfr_a1r.read_file()

    for ns in gfr_a1.students:
        callback(ns, gfr_a1r.get_student_for_unique_utorid(ns.utorid))

if __name__ == '__main__':
    import os
    from os import system
    from os import listdir
    #look_for_missing_marks(gfr_a1=GradeFileReaderWriter("/tmp/a1"), gfr_a1r=GradeFileReaderWriter("/tmp/a1r"), callback=check_a1_a1r)
    gfr_a2=GradeFileReaderWriter("/tmp/a2").read_file()
    gfr_a2r=GradeFileReaderWriter("/tmp/a2r").read_file()
    for ns in gfr_a2.students:
        #print(ns)
        check_a2_a2r(ns, gfr_a2r.get_student_for_unique_utorid(ns.utorid))
