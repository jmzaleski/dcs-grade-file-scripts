'''
Created on Apr 5, 2016

@author: mzaleski
'''

import matz_utils
import csv

class MapFileReader(object):
    '''
    classdocs
    '''

    def __init__(self, fn, separator_char):
        '''
        Create a reader for files mapping one string to another.
        parameter gives the field separator character, typically space, tab, or comma
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.separtor_char = separator_char
        self.cdfid_to_github = None
        try:
            self.map_file = open(fn,'rb')
        except:
            self.msg.error("failed to open", fn)
        
    def readMap(self):
        "returns a dictionary mapping the first field to the second"
        map_reader = csv.reader(self.map_file, delimiter=self.separtor_char, quotechar='|',dialect=csv.excel_tab)
        first_line = True
        self.cdfid_to_github = {}
        #read the mapping file and create a map from LOWER CASE cdfid to github id
        for l in map_reader:
            if first_line:
                first_line = False
                continue
            key = l[0]
            val = l[1]
            self.msg.debug("readMap",key,val)
            self.cdfid_to_github[key.lower()] = val
        return self.cdfid_to_github   
    
if __name__ == "__main__" :
    print ("instantiate MapFileReader")
    me = MapFileReader("cdfid-to-githubid.csv",',')
    map = me.readMap()
    for l in map:
        (key,val) = (l[0],l[1])
    print("key", key, "val", val, "map", map)
    
        