from __future__ import print_function  # allows print as function

import csv  # see https://docs.python.org/2/library/csv.html
import sys

class DdahAllocation:
    """like line in the DDAH form, describes one of the duties a TA's
    time will be allocated to. Eg. 'marking 31 a1 estimated to take 5 min each'
    """
    ID = 0
    def __init__(self,duty_description,duty_type,quantity,durationInMinutes):
        self.id = DdahAllocation.ID
        DdahAllocation.ID +=1
        self.duty_description = duty_description            #eg grade a1
        self.duty_type = duty_type  #eg Marking
        self.quantity = quantity    #31
        self.duration_in_minutes = durationInMinutes

    def __str__(self):
        return "ID=%d Q=%d, C=%s, %s D=%d hours=%g " % (self.id, self.quantity, self.duty_type,
                                                    self.duty_description,self.duration_in_minutes,
                                                    float(self.quantity * self.duration_in_minutes / 60.0))



class Ddah:
    "Description of Duties and Hockey for a single student"
    def __init__(self, name, utorid,category,allocations):
        self.name = name
        self.utorid = utorid
        self.category = category
        self.allocations = allocations #list of DdahAllocation instances

    def __str__(self):
        s = "TA_name=%s utorid=%s tutorial_category=%s" % (self.name, self.utorid, self.category)
        for a in self.allocations:
            s += "\n  "
            s += str(a)
        return s
    
class ReadInstructorDdahCSV:
    """Class to manage reading one of the files that Karen was emailed
    corresponding to the DDAH of an entire class and creating a Ddah object from the
    line representing each student
    """
    def __init__(self, file_name):
        self.VERBOSE = False #debug
        self.FN = file_name
        self.duty_descriptions = [] #row on the form giving the "type of allocation"
        self.rows = [] #row        #raw rows describing each TA
        self.duty_categories = []
        #maps the strings the instructors were asked to describe kind of duty
        #to the letters the DDAH importer needs to see.
        self.DUTY_TO_MM = { #short for michelle map :)
            'Training' : 'A',
            'Additional Training (if required)':'B',
            'Preparation': 'C',
            'Marking/Grading' : 'D',
            'Contact Time': 'D',
            'Other Duties': 'E'
            }
        #inverse..
        self.MM_TO_DUTY = {}
        for cat in self.DUTY_TO_MM:
            key = cat
            val = self.DUTY_TO_MM[cat]
            self.MM_TO_DUTY[val] = key

        #print(self.MM_TO_DUTY, self.DUTY_TO_MM)
            
        
    def readInstructorCSV(self):
        """
        read the file and squirrel away data in it.
        First line is the names the of the duties the instructor has chosen,
        Second line is the dutytype
        Following are as many lines as instructor expects TAs
        with the number of HOURS (!) estimated the duty will require.
        (No quantity, no minutes, basically quantity * minutes baked in)
        """
        with open(self.FN, 'r') as csvfile:
            csv_file_reader = csv.reader(csvfile, delimiter=',', quotechar='|',dialect=csv.excel_tab)
            raw_line = next(csv_file_reader)
            assert( raw_line[0] == "Name")
            assert (raw_line[1] == "Email")
            assert (raw_line[2] == "Total Hours")
            assert (raw_line[3] == "Tutorial Category")
            self.duty_descriptions = raw_line[4:]
            first_line = True
            for row in csv_file_reader:
                if len(row) == 0:
                    continue #just skip the damn empty lines
                if first_line:
                    assert(row[0] == '')
                    self.duty_categories = row[4:]
                    first_line = False
                    continue
                self.rows += [row]  #name, utorid, total_hours then estimate in hours
                
    def toDdah(self):
        "convert what we read into a DDAH instance. to do so parse raw rows read previously"
        ddahList = []
        for r in self.rows:
            ta_name = r[0]
            ta_utorid = r[1]
            total_hours = r[2]
            tutorial_category = r[3] #nb unset for 369
            #rest of row contains estimates of how long duties will take
            estimated_hours = r[4:]
            if self.VERBOSE:
                print('TA name:',ta_name)
                print('utorid:',ta_utorid)
                print('total_hours:',total_hours)
                print('tutorial_category:',tutorial_category)
                print('estimated_hours:',estimated_hours)
                print("self.duty_descriptions:",self.duty_descriptions)
                print("self.duty_categories:",self.duty_categories)
                print(next(zip(estimated_hours, self.duty_descriptions, self.duty_categories)))

            # create an allocation for each duty for which an time estimate is found
            allocations = []
            for (hour,duty_description,duty_cat) in zip(estimated_hours, self.duty_descriptions, self.duty_categories):
                if len(hour) == 0:
                    continue
                a = DdahAllocation(duty_description, duty_cat, 1.0, float(hour) * 60.0)
                if self.VERBOSE:
                    print("hours:",hour, "desc:", duty_description, "category:", duty_cat, "mmcat:", self.DUTY_TO_MM[duty_cat])
                    print(a)
                allocations.append(a)
            ddah = Ddah(ta_name, ta_utorid, tutorial_category, allocations)
            if self.VERBOSE:
                print(ddah)
            ddahList.append( ddah)
        if self.VERBOSE:
            print(ddahList)
        return ddahList

    def __str__(self):
        "fixme"

    def dump(self):
        print(self.DUTY_TO_MM)
        print(self.MM_TO_DUTY)
        print(self.duty_descriptions)
        print(self.duty_categories)
        print('--- data ---');
        for r in self.rows:
            print(r)
        
if __name__ == '__main__':

    if len(sys.argv) == 2 :
        fn = sys.argv[1]
    else:
        msg.warning( "usage: ", sys.argv[0], "instructor-csv-file-name")
        exit(2)
    
    me = ReadInstructorDdahCSV(fn)
    me.readInstructorCSV()
    ddahList = me.toDdah()
    for ddah in ddahList:
        print(ddah)

                 
