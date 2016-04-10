'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import matz_utils

class CdfClassFileStudentRecord:
    "the information in each line of a CDF class file"
    def __init__(self, dropped, flag, student_number, cdfid ):
        self.is_dropped = dropped
        self.flag = flag
        self.student_number = student_number
        self.cfgid = cdfid

    def get_is_dropped(self):
        return self.__is_dropped


    def get_flag(self):
        return self.__flag


    def get_student_number(self):
        return self.__student_number


    def get_cdfid(self):
        return self.__cdfid


    def set_is_dropped(self, value):
        self.__is_dropped = value


    def set_flag(self, value):
        self.__flag = value


    def set_student_number(self, value):
        self.__student_number = value


    def set_cdfid(self, value):
        self.__cdfid = value


    def del_is_dropped(self):
        del self.__is_dropped


    def del_flag(self):
        del self.__flag


    def del_student_number(self):
        del self.__student_number


    def del_cdfid(self):
        del self.__cdfid

        
    def cdfid(self):
        return self.cdfid
    #eclipse did this. i don't really khnow what it means
    is_dropped = property(get_is_dropped, set_is_dropped, del_is_dropped, "is_dropped's docstring")
    flag = property(get_flag, set_flag, del_flag, "flag's docstring")
    student_number = property(get_student_number, set_student_number, del_student_number, "student_number's docstring")
    cdfid = property(get_cdfid, set_cdfid, del_cdfid, "cdfid's docstring")
        
class CdfClassListFileReader:
    '''
    read cdf class list files (the files that live in cdf.toronto.edu:/u/csc/instructors/classlists)
    '''

    def __init__(self, fn):
        "constructor for CdfClassListFileReader takes file name"
        self.msg = matz_utils.MessagePrinter(True)
        self.msg.setPrefix("CdfClassListFileReader")
        
        try:
            self.cdf_file = open(fn, 'rb')
        except:
            print("eh?",fn)
            self.msg.error("failed to open", fn)
        self.cdfid_to_name_map = {}
    
    def extractCdfid(self, line):
        (d,csvfields) = self.extractDataFields(line)
        cdfid = csvfields[0]
        self.msg.debug(d,cdfid)
        return (d,cdfid)
    
    #example line from a CDF class lst file:
    #g5matz  771734894 (Zaleski, Mathew) matz@cs.toronto.edu
    #
    def extractCdfidName(self, line):
        "returns tuple (cdfid, name)"
        #self.msg.debug("EXTRACT",line)
        tokens_left = line.split('(')[0]  #g5matz  771734894 
        cdfid = tokens_left.split(' ')[0] #g5matz  771734894 (Zaleski, Mathew) matz@cs.toronto.edu

        tokens_right = line.split('(')[1] #Zaleski, Mathew) matz@cs.toronto.edu
        name = tokens_right.split(')')[0]  #Zaleski, Mathew
        #student number is a bit harder, may be one or two blanks
        self.msg.debug("extractDataField name ", name)
        self.msg.debug("extractDataField cdfid ", cdfid)
        return (cdfid, name)
    
    def parseClassListLine(self, line):
        "returns tuple (cdfid,name,email) for a line from a CDF class list file"
        print(line)
        cdfid_number_rest = line.split("(")
        name_email = cdfid_number_rest[1].split(")")
        cdfid = cdfid_number_rest[0].split(" ")[0]
        student_number = cdfid_number_rest[0].split(" ")[1]
        self.msg.debug("no use for student number, so far", student_number)
        name = name_email[0] 
        email = name_email[1]
        return(cdfid,name,email)    


    def readLines(self):
        lines = []
        for rawline in self.cdf_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            lines.append(line) 
            self.msg.debug("READLINES", line)
        return lines

    def cdfid_to_name(self, cached_lines):
        for line in cached_lines:
            (cdfid,name) = self.extractCdfidName(line)
            self.cdfid_to_name_map[cdfid] = name
        return self.cdfid_to_name_map
    
if __name__ == "__main__" :
    print ("instantiate ClassListFileReader")
    me = CdfClassListFileReader("CSC302H1S")
    ls = me.readLines()
    cdfid_to_name = me.cdfid_to_name(ls)
    for l in ls:
        (cdfid,name) = me.extractCdfidName(l)
        print("cdfid", cdfid, "name", name, "cdfid_to_name", cdfid_to_name[cdfid])


            
