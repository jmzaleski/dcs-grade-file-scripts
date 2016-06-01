'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import matz_utils

class CdfClassFileStudentRecord:
    "the information in each line of a CDF class file"
    def __init__(self, cdfid, student_number, name, email ):
        self.cdfid = cdfid
        self.student_number = student_number
        self.name = name
        self.email = email
    def __str__(self):
        return "CdfClassFileStudentRecord cdfid %s student_number %s name %s email %s" %  (self.cdfid,self.student_number,self.name, self.email)
    
    def get_cdfid(self):
        return self.__cdfid
    def get_student_number(self):
        return self.__student_number
    def get_name(self):
        return self.__name
    def get_email(self):
        return self.__email
    def set_cdfid(self, value):
        self.__cdfid = value
    def set_student_number(self, value):
        self.__student_number = value
    def set_name(self, value):
        self.__name = value
    def set_email(self, value):
        self.__email = value
    def del_cdfid(self):
        del self.__cdfid
    def del_student_number(self):
        del self.__student_number
    def del_name(self):
        del self.__name
    def del_email(self):
        del self.__email

    cdfid = property(get_cdfid, set_cdfid, del_cdfid, "cdfid's docstring")
    student_number = property(get_student_number, set_student_number, del_student_number, "student_number's docstring")
    name = property(get_name, set_name, del_name, "name's docstring")
    email = property(get_email, set_email, del_email, "email's docstring")

        
class CdfClassListFileReader:
    '''
    read cdf class list files (the files that live in cdf.toronto.edu:/u/csc/instructors/classlists)
    '''

    def __init__(self, fn):
        "constructor for CdfClassListFileReader takes file name"
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("CdfClassListFileReader")
        try:
            self.cdf_file = open(fn, 'rb')
        except:
            self.msg.error("failed to open", fn)
        self.cdfid_to_name_map = {}
    
    def extractCdfid(self, line):
        rec = self.parseClassListLine(line)
        return (rec.cdfid, rec.name) 
    
    # g5matz   773174940 (Zaleski, Mathew) matz@cs.toronto.edu
    #
    def parseClassListLine(self, line):
        "returns instance of CdfClassFileStudentRecord"
        cdfid_number___rest = line.split("(")            # [ "g5matz    771734940", "Zaleski Mathew) matz@cs.toronto.edu"]
        cdfid_sn = cdfid_number___rest[0].split(" ")     # [ "g5matz",,,    "771734940"]
        name_email = cdfid_number___rest[1].split(")")   # [ "Zaleski Mathew", "matz@cs.toronto.edu"]
        
        cdfid = cdfid_sn[0]
        student_number = "" #cdfid_sn[-1-1]                  # really should search for non
        for s in cdfid_sn[1:]:
            if len(s) != 0:
                student_number = s
                break
        assert len(student_number) != 0 
        self.msg.debug("no use for student number, so far", student_number)
        name = name_email[0] 
        email = name_email[1]
        return CdfClassFileStudentRecord(cdfid,student_number,name,email)
    
    def readLines(self):
        lines = []
        for rawline in self.cdf_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            lines.append(line) 
            self.msg.debug("READLINES", line)
        return lines

    def cdfid_to_name(self, cached_lines):
        for line in cached_lines:
            rec = self.parseClassListLine(line)
            #(cdfid,name) = self.extractCdfidName(line)
            self.cdfid_to_name_map[rec.cdfid] = rec.name
        return self.cdfid_to_name_map
    
if __name__ == "__main__" :
    print ("instantiate ClassListFileReader")
    me = CdfClassListFileReader("CSC2702HY")
    ls = me.readLines()
    cdfid_to_name = me.cdfid_to_name(ls)
    for l in ls:
        rec = me.parseClassListLine(l)
        print(rec)
        print("cdfid", rec.cdfid)
        print("name", rec.name)
        print("student_number", rec.student_number)
        print("email", rec.email)


            
