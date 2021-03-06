from __future__ import print_function  # allows print as function

import csv  # see https://docs.python.org/2/library/csv.html
import sys
import traceback
    

class DdahAllocation:
    """like line in the DDAH form, describes one of the duties a TA's
    time will be allocated to. Eg. 'marking 31 a1 estimated to take 5 min each'
    """
    ID = 0
    def __init__(self,duty_description,duty_type,quantity,durationInMinutes):
        self.id = DdahAllocation.ID
        DdahAllocation.ID +=1
        self.duty_description = duty_description            #eg "grade a1"
        self.duty_type = duty_type                          #eg Marking
        self.quantity = quantity                            #31 (students in TA's section)
        self.duration_in_minutes = durationInMinutes

    def __str__(self):
        return "ID=%d Q=%d, C=%s, %s D=%d hours=%6.2f " % (self.id, self.quantity, self.duty_type,
                                                    self.duty_description,self.duration_in_minutes,
                                                    float(self.quantity * self.duration_in_minutes / 60.0))

class Ddah:
    "Description of Duties and Hockey for a single student"
    def __init__(self, name, utorid, total_hours, category,allocations):
        self.name = name
        self.utorid = utorid
        self.total_hours = total_hours
        self.category = category   #training category? eg: meeting with supervisor?
        self.allocations = allocations #list of DdahAllocation instances

    def totalMin(self):
        "add up minutes estimated for all allocations"
        total = 0.0
        for a in self.allocations:
            total += (a.quantity * a.duration_in_minutes)
        return total

    def totalHours(self):
        return self.totalMin() / 60.0

    def __str__(self):
        s = "TA_name=%s utorid=%s total_hours=%5.2f tutorial_category=%s" % (self.name, self.utorid, self.total_hours, self.category)
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
        self.duty_types = []
        #maps the strings the instructors were asked to describe kind of duty
        #to the letters the DDAH importer needs to see.

        self.DUTY_TO_MM = { #MM short for "michelle map" :)
            'Training'                          : 'A',
            'Additional Training (if required)' : 'B',
            'Preparation'                       : 'C',
            'Contact Time'                      : 'D',
            'Marking/Grading'                   : 'E',
            'Other Duties'                      : 'F'
            }

        self.SKILL_CATEGORY_TO_MM = {
            "Discussion-based Tutorial"  :"A",
            "Skill Development Tutorial" :'B',
            "Review and Q&A Session"     :'C',
            "Laboratory/Practical"       :'D'
            }

        self.TRAINING_TO_MM = {
            "Attending Health and Safety training session"                     : "A",
            "Meeting with supervisor"                                          : "B",
            "Adapting Teaching Techniques (ATT) (scaling learning activities)" : "C"
            }



        
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
            raw_first_line  = next(csv_file_reader)
            assert( raw_first_line[0] == "Name")
            assert (raw_first_line[1] == "Email")
            assert (raw_first_line[2] == "Total Hours")
            assert (raw_first_line[3] == "Tutorial Category")
            self.duty_descriptions = raw_first_line[4:]
            first_line = True
            for row in csv_file_reader:
                if self.VERBOSE: print("readInstructor", row)
                if len(row) == 0:
                    continue #just skip the damn empty lines
                empty = True
                for each_col in row:
                    if len(each_col)>0:
                        empty = False
                if empty:
                    continue
                if first_line:
                    assert(row[0] == '')
                    self.duty_types = row[4:]
                    first_line = False
                    continue
                self.rows += [row]  #name, utorid, total_hours then estimate in hours
                
    def toDdah(self):
        "convert each row into a DDAH instance. parse raw rows read previously"
        ddahList = []
        ix = 0
        for r in self.rows:
            try:
                ta_name = r[0]
                ta_utorid = r[1]
                total_hours = float(r[2])
                training_category = r[3] #nb unset for 369
                #rest of row contains estimates of how long duties will take
                estimated_hours = r[4:]

                # create an allocation for each duty for which an time estimate is found
                allocations = []
                for (hour,duty_description,duty_cat) in zip(estimated_hours, self.duty_descriptions, self.duty_types):
                    if self.VERBOSE: print("zip","``%s''"% hour,"``%s''"% duty_description,"``%s''"% duty_cat)
                    
                for (hour,duty_description,duty_cat) in zip(estimated_hours, self.duty_descriptions, self.duty_types):
                    if len(hour) != 0: 
                        a = DdahAllocation(duty_description, duty_cat, 1.0, float(hour) * 60.0)
                        #if self.VERBOSE: print(a)
                        allocations.append(a)
                ddah = Ddah(ta_name, ta_utorid, total_hours, training_category, allocations)
                ddahList.append( ddah)
                if self.VERBOSE: print("toDdah",ddah)
                ix +=1
            except:
                print("parsing rows failed on row", ix, r,file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                        
        return ddahList

    def writeTappDdahCSV(self, ddahList, course_aka_position, supervisor_utorid, round_id, ofn):
        "write out the ddah as a CSV file in the format tapp can import"
        empty_cell = ['']
        #this import season we need to guess this. karen will edit sheet written by this script when necessary
        HACK_DEFAULT_TUTORIAL_CATEGORY = "Skill Development Tutorial"
        prefix_cols = [''] * 5

        with open(ofn, 'w') as csvfile:
            ddah_csv_writer = csv.writer(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            ddah_csv_writer.writerow( ["supervisor_utorid",supervisor_utorid])
            ddah_csv_writer.writerow( ["course_name",course_aka_position])
            ddah_csv_writer.writerow( ["round_id",round_id])
            ddah_csv_writer.writerow( ["duties_list",'','',"trainings_list",'','',"categories_list"])

            ddah_csv_writer.writerow( ["Training",                         "A",'',  "Attending Health and Safety training session","A",'',                    "Discussion-based Tutorial","A",''])
            ddah_csv_writer.writerow( ["Additional Training (if required)","B",'',  "Meeting with supervisor","B",'',                                         "Skill Development Tutorial",'B'])
            ddah_csv_writer.writerow( ["Preparation",                      "C",'',  "Adapting Teaching Techniques (ATT) (scaling learning activities)","C",'',"Review and Q&A Session",'C'])
            ddah_csv_writer.writerow( ["Contact Time",                     "D",'',  '','','',                                                                 "Laboratory/Practical",'D'])         
            ddah_csv_writer.writerow( ["Marking/Grading","E",''])
            ddah_csv_writer.writerow( ["Other Duties","F",''])
            ddah_csv_writer.writerow( empty_cell )

            for ddah in ddahList:
                if self.VERBOSE: print("writeTappDdah",ddah)
                    
                if len(ddah.category) == 0:
                    ddah.category = HACK_DEFAULT_TUTORIAL_CATEGORY
                    
                broken = False
                if not ddah.category in self.SKILL_CATEGORY_TO_MM:
                    print("``%s''" % ddah.category, 'not valid skill category',file=sys.stderr)
                    broken = True
                for a in ddah.allocations:
                    if not a.duty_type in self.DUTY_TO_MM:
                        broken = True
                        print(ddah.name, ddah.utorid, 'duty type ', "``%s''" % a.duty_type, 'not valid',str(a),file=sys.stderr)
                if broken:
                    raise Exception("quitting due to errors in allocation:" )

                total = ddah.totalHours()
                num_units_row = [ ddah.name, ddah.utorid, ddah.total_hours, '','','num_units']
                unit_name_row = empty_cell * 2 + ["total_hours","categories",'','unit_name']
                duty_id_row   = empty_cell * 2 + [total] + [self.SKILL_CATEGORY_TO_MM[ddah.category]] + empty_cell + ['duty_id']  #HACK.. sometimes fix B to C by hand?
                minutes_row   = prefix_cols + ['minutes']
                hours_row     = prefix_cols + ['hours']
                    

                ddah_csv_writer.writerow([ "applicant_name", "utorid", "required_hours","trainings","allocations",'id(generated)'])
                for a in ddah.allocations:
                    num_units_row += ["%d" % a.quantity]
                    unit_name_row += ["%s" % a.duty_description]
                    duty_id_row   += ["%s" % self.DUTY_TO_MM[a.duty_type]]
                    minutes_row   += ["%d" % a.duration_in_minutes]
                    hours_row     += ["%d" % (a.quantity * a.duration_in_minutes)]

                for row in [num_units_row, unit_name_row, duty_id_row, minutes_row, hours_row]:
                    ddah_csv_writer.writerow(row)

    def __str__(self):
        str(self.DUTY_TO_MM) + str(self.duty_descriptions) + str(self.duty_types) + str(self.rows)

    def dump(self):
        print(self.DUTY_TO_MM)
        print(self.duty_descriptions)
        print(self.duty_types)
        print('--- data ---');
        for r in self.rows:
            print(r)
        
if __name__ == '__main__':

    if len(sys.argv) == 6 :
        course_aka_position = sys.argv[1]
        supervisor_utorid = sys.argv[2]
        round_id = sys.argv[3]
        fn = sys.argv[4]
        ofn = sys.argv[5]
    else:
        print( "usage: ", sys.argv[0], "course_aka_position supervisor_id round_id instructor-csv-file-name output-tapp-csv-file-name",file=sys.stderr)

    try:
        me = ReadInstructorDdahCSV(fn)
    except:
        print("reading", fn, "threw",file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        exit(1)

    try:
        me.readInstructorCSV()
    except:
        print("parsing ddah csv info threw",file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        exit(2)
        
    try:
        me.writeTappDdahCSV(me.toDdah(),course_aka_position,supervisor_utorid,round_id,ofn)
    except:
        print(sys.argv[0], "python import script threw..",file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        exit(2)

    exit(0)
    
