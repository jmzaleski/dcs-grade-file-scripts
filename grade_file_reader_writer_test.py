'''
Created on Mar 4, 2017

@author: mzaleski
'''
import unittest
from grade_file_reader_writer import GradeFileReaderWriter
import platform
from unittest.mock import mock_open, patch

class Test(unittest.TestCase):

    #TODO: this is meant to be passed into a mock open.. but if it's a string the reading code can't decode it
    test_data = """
*/,
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

0771734940    MathewZaleski,jmzaleski,Zteam,TAX,Zaleski,J Mathew,matz@cs.toronto.edu,2
"""
    def setUp(self):
        #print(self.test_data)
        self.gfrw = GradeFileReaderWriter("test-inputs/grade-file", debug=True)
        print("run pyunit tests using python version", platform.python_version())
        
    def testName(self):
        
        with patch('%s.open' % "grade_file_reader_writer", mock_open(read_data=self.test_data), create=True) as m:
            self.gfrw.read_file()
            for student in self.gfrw.students:
                print(student)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    import os
    print(os.getcwd())
    unittest.main()