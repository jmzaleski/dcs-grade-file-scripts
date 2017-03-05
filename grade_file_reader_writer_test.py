'''
Created on Mar 4, 2017

@author: mzaleski
'''
import unittest
from grade_file_reader_writer import GradeFileReaderWriter
import platform
from unittest.mock import mock_open, patch
import re

class Test(unittest.TestCase):

    #TODO: this is meant to be passed into a mock open.. but if it's a string the reading code can't decode it
    test_data = """*/,
* weird line above changes the separator char to , (comma). 
utorid  "    * string utorid       $2
githubid "   * string githubid     $3
team "       * project team id     $4
ta   "       * tutor               $5
ln   "       * last name           $6
fn   "       * first names         $7 
email "      * email               $8         
a1   / 3     * gimme set up VM
* next line must be blank in this header

0771734940    MathewZaleski,zaleskim,jmzaleski,Zteam,TAX,Zaleski,J Mathew,matz@cs.toronto.edu,2.0
0771734941    JaneDoe,utoridjdoe,jdoe,Zteam,TAX,Doe,Jane,jane.doe@mail.utoronto.ca,3
0771734942    JohnSmith,utoridjsmith,jsmith,Zteam,TAX,Smith,John,john.smith@mail.utoronto.ca,1
0771734943    Mr NoA1, utoridnoa1,githubnoa1,Zteam,TAX,NoA1Surname,Noa1fn,no.a1@mail.utoronto.ca,
"""
    def setUp(self):
        #print(self.test_data)
        #contents_of_grade_file = open("test-inputs/grade-file").read()
        self.gfrw = GradeFileReaderWriter(self.test_data, debug=True)
        
    def testName(self):
        #trick open into reading from the mock.. but maybe we should just pass the string into the constructor
        #with patch('%s.open' % "grade_file_reader_writer", mock_open(read_data=self.test_data), create=True) as m:
        self.gfrw.read_file()
        #for student in self.gfrw.student_generator(lambda student: True):
        #    print(student)
        for student in self.gfrw.student_generator(lambda student: re.compile("zaleski", re.IGNORECASE).match(student.ln)):
            print(student)
            assert(student.githubid == "jmzaleski")
            assert(student.utorid == "zaleskim")
            assert(student.ln == "Zaleski")
            assert(student.team == "Zteam")
            assert(student.ta == "TAX")
            assert(student.fn == "J Mathew")
            assert(student.email == "matz@cs.toronto.edu")
            assert(type(student.a1) is float)
            assert(student.a1 == 2)
        #missing data are None, so we look for students for whom a1 is not None.
        sum = 0.0
        n=0
        for student in self.gfrw.student_generator(lambda student: student.a1):
            sum += student.a1
            print(student.ln,student.a1)
            n += 1
        avg = sum/n
        print("average a1", avg)
        assert(n == 3)
        assert(avg == 2)
        
if __name__ == "__main__":
    import os
    print(os.getcwd())
    print("run pyunit tests using python version", platform.python_version())
    unittest.main()