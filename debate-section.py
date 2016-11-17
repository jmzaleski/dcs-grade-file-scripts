import os,sys

sys.path.append('../../bin')

from grade_file_reader_writer import GradeFileReaderWriter
#from zip_assignments_for_ta import zip_assignments_for_ta

empty = GradeFileReaderWriter("CSC300H1F-empty")
empty.read_file()
#print (empty.students)
utorid_to_student_map = {}
for s in empty.students:
    utorid_to_student_map[s.utorid] = s

print(len(sorted(utorid_to_student_map.keys())))

#crypto,allinico,ansermin
fn = 'debate-signup/debate.csv'

with open(fn, 'r') as csv_file:
    import csv
    csv_file_reader = csv.reader(csv_file, delimiter=',')
    for student_record in csv_file_reader:
        if len(student_record[0]) == 0:
            print("reject because first field is empty",student_record)
        try:
            (topic, utorid1, utorid2) = (student_record[0],student_record[1],student_record[2])
            if not utorid2:
                print("no pair in", student_record)
                continue
            #print(topic, utorid1, utorid2) 
        except:
            print("oops", student_record)

        try:
            if not utorid1 in utorid_to_student_map:
                print(utorid1,'not in classlist')
                exit(1)
            if not utorid2 in utorid_to_student_map:
                print(utorid2,'not in classlist')
                exit(1)

            s1 = utorid_to_student_map[utorid1]
            section1 = s1.sec
            #print(utorid1, section1)
            s2 = utorid_to_student_map[utorid2]
            section2 = s2.sec
            if section1 != section2:
                print("not from same section", utorid1, utorid2, section1, section2)
                continue
            #print(utorid2, section2)
            print("%s,%s,%s,%s,%s" % (topic,utorid1,section1,utorid2,section2))
        except:
            print("oops", student_record, s1, section1 )
            exit(0)
    


