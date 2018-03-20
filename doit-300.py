#!/opt/local/bin/python3.5

EMPTY="CSC300H1S-empty"
R_EMPTY="r-empty"        # yucky hack a grades file listing all the reading submissions

# collect all reading submission marks in this file
READ="read"

TERM = "term"   # term marks will be gcopy'd into this file
FINAL = "fin"   # name of final grades file AND also the name of the forumula that calculates it

LIST=[
    "a1",    # downloaded from a1r google sheet   (using fetch_ta_marks.py)
    "a2",    # downloaded from a2r google sheet   (using fetch_ta_marks.py)
#    "a3",
#    "deb",
    "p_tu",  # downloaded from tutorial-participation sheet  (using fetch_ta_marks.py)
#    "a4",
    # "exam"
    "r"
    ]

def mark_file_name_generator3(quiz_dir,suffix,list):
    "generator that turns mark names into file names following convention that have same suffix"
    return ((m,m+suffix) for m in sorted(list))
    
import sys
sys.path.append('/home/matz/git/dcs-grade-file-scripts')
sys.path.append('/Users/mzaleski/git/dcs-grade-file-scripts')

from os import system
import os
import shutil
import itertools

if not os.path.isfile(EMPTY):
    print("cannot stat",EMPTY)
    exit(5)

if not os.path.isfile(R_EMPTY):
    print("cannot stat",R_EMPTY)
    exit(5)

# this script must be run from directory containing grades files    
mark_dir = os.path.abspath(".")

# relative path from here to where jim clark tools live
GBIN = "../../grades-bin/"
import jim_clark_tools

jim_clark_tools.init(mark_dir,GBIN)

def backup_fn(ofn):
    modifiedTime = os.path.getmtime(ofn) 
    import datetime
    timestamp = datetime.datetime.fromtimestamp(modifiedTime).strftime("%b-%d-%Y_%H.%M.%S")
    return "%s-%s" % (ofn,timestamp)

def backup_if_exists(ofn):
    import os
    if not os.path.isfile(ofn):
        return
    back_ofn = "./backup/" + backup_fn(ofn)
    # modifiedTime = os.path.getmtime(ofn) 
    # import datetime
    # timestamp = datetime.datetime.fromtimestamp(modifiedTime).strftime("%b-%d-%Y_%H.%M.%S")
    # back_ofn = "backup/%s-%s" % (ofn,timestamp)
    print("back up %s to %s" % (ofn, back_ofn))
    os.rename(ofn, back_ofn)
    return back_ofn

def check_input_grades_files():
    # check if grades files exist, glint clean
    print('glinting.. ', end='')
    sys.stdout.flush()
    for (m,fn) in itertools.chain(
#            mark_file_name_generator3(mark_dir,"-0101",R1),
#            mark_file_name_generator3(mark_dir,"-5101",R5),
            mark_file_name_generator3(mark_dir,"",LIST)
            ):
        if not os.path.isfile(fn):
            print("no file ", fn)
            exit(3)
        if jim_clark_tools.glint(fn) == 0:
            print(fn+"..", end='')
            sys.stdout.flush()
        else:
            print("glint",fn,"non-clean, exit..")
            exit(5)
    print("")
    
def calculate_reading_grade(r1,r5,r_empty,read):
    "readings accumulated into arg"
    #R starts off as the empty marks file (with all mark fields defined)
    from runit import runit
    backup_if_exists(read)
    if shutil.copy(r_empty, read): #src, dest
        runit("ls -l %s" % read)
    else:
        print("failed to copy",r_empty,"to",read)
        exit(5)

    # gcopy copies the reading mark for each week into grade file read
    for (m,fn) in itertools.chain(
            mark_file_name_generator3(mark_dir,"-0101",r1),
            mark_file_name_generator3(mark_dir,"-5101",r5)
            ):
        print("about to: gcopy", m,"from",fn,"to", read)
        if jim_clark_tools.gcopy(m,fn,read):
            print("gcopy", m, fn, read, "has failed")
            exit(0)
    #generats r, the total reading/lec participation mark
    jim_clark_tools.gen(read) 

def calculate_term_grade():
    "once all the grades are down, calculate the term grade"
    from runit import runit
    if shutil.copy(EMPTY, TERM): #src, dest
        runit("ls -l %s" % TERM)
    else:
        print("failed to copy",EMPTY,"to",TERM)
        exit(5)
    # term mark needs r too
    for (m,fn) in itertools.chain( mark_file_name_generator3(mark_dir,"",LIST + [READ]) ):
        if jim_clark_tools.gcopy(m,fn,TERM):
            print("gcopy", m, fn, TERM, "has failed")
    jim_clark_tools.gen(TERM)

def calculate_term_grade2(mark_dir,empty, mark_list, term):
    "once all the grades are down, calculate the term grade"
    from runit import runit
    backup_if_exists(term)
    if shutil.copy(empty, term): #src, dest
        runit("ls -l %s" % term)
    else:
        print("failed to copy",empty,"to",term)
        exit(5)
    # term mark needs r too
    for (m,fn) in itertools.chain( mark_file_name_generator3(mark_dir,"",mark_list) ):
        if jim_clark_tools.gcopy(m,fn,term):
            print("gcopy", m, fn, term, "has failed")
    jim_clark_tools.gen(term)
    
def calculate_final_grade(term,exam_mark,exam_fn,fin):
    "exam too"
    from runit import runit
    backup_if_exists(fin)
    if shutil.copy(term, fin): #src, dest
        runit("ls -l %s" % fin)
    else:
        print("failed to copy",term,"to",term)
        exit(5)
    # add exam mark to term marks in fin
    if jim_clark_tools.gcopy(exam_mark,exam_fn,fin):
       print("gcopy", exam_mark, exam_fn, fin, "has failed")
    jim_clark_tools.gen(fin)

def clean_up_marks_file(fn):
    #clean up the junk so it's narrower
    jim_clark_tools.gremove(fn,"ta")
    jim_clark_tools.gremove(fn,"utorid")
    jim_clark_tools.gremove(fn,"sec")
    jim_clark_tools.gremove(fn,"fn")
    jim_clark_tools.gremove(fn,"ln")
    jim_clark_tools.gremove(fn,"email")
    
# REAL WORK: combine the assignment (etc) grades files into one term grades file
FIN="fin"
EXAM="exam-raw"
EXAM_MARK="exam"

check_input_grades_files()
#calculate_reading_grade(R1,R5,R_EMPTY,READ)
backup_if_exists(TERM)
calculate_term_grade2(mark_dir, EMPTY, LIST + [READ], TERM)

#jim_clark_tools.gstats(READ)
#print("tutorial grade (attendance) statistics")
#jim_clark_tools.gstats("p_tu")
   

backup_if_exists(FIN)
#calculate_final_grade(TERM,EXAM_MARK,EXAM,FIN)

term_to_post = TERM + "-cdf"
fin_clean = FIN + "-clean"

if True:
    if not shutil.copy(TERM, term_to_post): #src, dest
        exit(0)
    clean_up_marks_file(term_to_post)
    jim_clark_tools.gremove(term_to_post,"fin")
    jim_clark_tools.gremove(term_to_post,"exam")
    if not shutil.copy(FIN, fin_clean): #src, dest
        exit(0)
    clean_up_marks_file(fin_clean)

print("TERM grade statistics")
jim_clark_tools.gstats(term_to_post,width=6)
    
print("final grade statistics")
jim_clark_tools.gstats(fin_clean,width=6)

from runit import runit
runit("ls -ltr %s %s %s %s" % (TERM, term_to_post, FIN, fin_clean))

exit(0)    

