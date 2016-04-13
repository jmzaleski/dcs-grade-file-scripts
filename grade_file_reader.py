'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import matz_utils
import re
from numpy.oldnumeric.ma import new_take

class GradeFileReader:
    '''
    read grades files
    '''

    def __init__(self, fn):
        '''
        Constructor
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("GradeFileReader")
        self.cdfid_to_tut = {}
        try:
            self.grade_file = open(fn, 'rb')
        except:
            self.msg.error("failed to open", fn)
    
    def skipHeader(self):
        hdr_lines = []
        for line in self.grade_file:
            hdr_lines.append(line.rstrip())
            self.msg.debug("HEADER", line)
            if len(line) == 1:
                return hdr_lines
        raise Exception("oops didn't find empty line at end of grade file header")
    

    def extractCdfid(self, line):
        (d,csvfields) = self.extractDataFields(line)
        cdfid = csvfields[0]
        self.msg.debug(d,cdfid)
        return (d,cdfid)
    
    #a marks file contains lines like: 
    #999521673    c2kosamu,0101,AP
    def extractDataFields(self, line):
        "returns list of csv separated fields"
        #self.msg.debug("EXTRACT",line)
        tokens = line.split(' ')
        dropped = False
        for token in tokens[1:]:
            if len(token) == 0:
                continue
            if token == "d": #students who have dropped are marked such
                dropped = True
                continue
            #might be other flags too?
            if len(token) > 1:
                #we've found comman separated fields now
                return (dropped, token.split(","))
        self.msg.error("extractCdfid failed to find data fields in ", line)
        raise Exception("extractCdfid failed to find data fields in ", line)
    
    # worse, it can look like:
    # NNNNNNNN    c2matz   ,0101,TA
    #
    # returns: (dropped, flag_char, cdfid, section, ta)
    # 
    def parseEmptyGradeFileLine(self,line):
        sline = line.rstrip()
        first_blank = sline.find(' ')
        #next 4 chars are blank, drop indicator, flag chars..
        if not sline[first_blank] == ' ':
            self.msg.error("malformed line: no blank?", sline)
        assert sline[first_blank] == ' '    #always a blank after student number
        assert sline[first_blank+3] == ' '  #always a black before data fields
        if not sline[first_blank+4].isalpha(): #real data has to start after blank
            self.msg.error("malformed line: after flag, then blank, must come alpha at pos", first_blank+4, '"'+sline+'"')
        #TODO assert something here along lines of is character 
        drop_char = sline[first_blank+1]    #two chars of flags
        flag_char = sline[first_blank+2]
        dropped = drop_char == 'd'
        
        data_on_sline = sline[first_blank+4:]
        grade_file_tokens = data_on_sline.split(",")
        
        #eventually a class will come up soon when I don't have TA sections. to avoid mayhem:
        #perhaps better to return empty strings for fields past cdfid? 
        if len(grade_file_tokens) < 3:
            self.msg.error("weird line in grade file len(grade_file_tokens) < 3", line )
        cdfid = grade_file_tokens[0].rstrip()
        if cdfid == "c6samuem":
            self.msg.debug("break here..")
        section = grade_file_tokens[1].rstrip()
        ta = grade_file_tokens[2].rstrip()
        self.msg.debug(cdfid,ta)
        return (dropped, flag_char, cdfid, section, ta)
            

    def readLines(self):
        "read all the lines in the file"
        lines = []
        for rawline in self.grade_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            lines.append(line) 
            self.msg.debug("READLINES", line)
        return lines
    
    def checkCdfid(self, lines, cdfid_in_map):
        "test the data in cdfid_in_map. return a aList of cdfid's in the file not in cdfid_in_map"
        found_problem = False
        aList = []
        for line in lines:
            (dropped, cdfid) = self.extractCdfid(line)
            if dropped:
                continue
            if not cdfid in cdfid_in_map:
                found_problem = True
                aList.append(cdfid)
        return (found_problem, aList)
                
    def readAndAppendColumnFromMap(self,cached_lines, cdfid_to_newcolumn_value_map):
        "read the grades file and append value of dictionary to the csv data values "
        new_lines = []
        for line in cached_lines:
            (dropped, cdfid) = self.extractCdfid(line)
            val = "NA"
            if cdfid in cdfid_to_newcolumn_value_map:
                val = cdfid_to_newcolumn_value_map[cdfid]
                if dropped:
                    self.msg.warning("typo or race condition?", cdfid, "in groups but also marked as dropped") 
            self.msg.verbose("BODY CDFID", cdfid, val)
            new_line = line  +"," + val
            new_lines.append(new_line)
            self.msg.debug("BODY CDFID", new_line)
        return new_lines


if __name__ == "__main__" :
    print ("instantiate GradeFileReader")
    me = GradeFileReader("CSC302H1S-empty")
    me.skipHeader()
    msg = matz_utils.MessagePrinter(True)
    ls = me.readLines()
    for l in ls:
        (dropped1, cdfid1) = me.extractCdfid(l)
        (dropped, flag_char, cdfid, section, ta) = me.parseEmptyGradeFileLine(l)
        if not dropped1 == dropped:
            msg.error("dropped1",dropped1, "dropped", dropped)
        if not cdfid1 == cdfid:
            msg.error("cdfid1", cdfid1, "cdfid", cdfid)
        print( "dropped", dropped, "cdfid", cdfid,"section", section, "ta", ta ) 
            
