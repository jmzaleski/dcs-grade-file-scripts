#!/opt/local/bin/python3.5

EMPTY="CSC300H1S-empty"
TERM = "term"   # term marks will be gcopy'd into this file
FINAL = "fin"   # name of final grades file AND also the name of the forumula that calculates it

# downloaded from google sheet in ta-marks (using fetch_a_sheet.py)
LIST=[
    "r",
    "p_tu",
    "a1r",
    "a2r", 
#    "a3",
#    "deb",
#    "a4",
    # "exam"
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
    for (m,fn) in mark_file_name_generator3(mark_dir,"",LIST):
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
    

def calculate_term_grade(mark_dir,empty, mark_list, term):
    "once all the grades are down, calculate the term grade"
    from runit import runit
    backup_if_exists(term)
    if shutil.copy(empty, term): #src, dest
        runit("ls -l %s" % term)
    else:
        print("failed to copy",empty,"to",term)
        exit(5)
    # term mark needs r too
    for (m,fn) in mark_file_name_generator3(mark_dir,"",mark_list):
        if jim_clark_tools.gcopy(m,fn,term):
            print("gcopy", m, fn, term, "has failed")
            exit(4)
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

check_input_grades_files()
backup_if_exists(TERM)
calculate_term_grade(mark_dir, EMPTY, LIST, TERM)

#jim_clark_tools.gstats(READ)
#print("tutorial grade (attendance) statistics")
#jim_clark_tools.gstats("p_tu")
   
# before exam why bother (apart from testing this script)
do_fin = False

if do_fin:
    FIN="fin"
    EXAM="exam-raw"
    EXAM_MARK="exam"
    fin_clean = FIN + "-clean"
    backup_if_exists(FIN)
    calculate_final_grade(TERM,EXAM_MARK,EXAM,FIN)

term_to_post = TERM + "-cdf"

if not shutil.copy(TERM, term_to_post): #src, dest
    exit(0)
clean_up_marks_file(term_to_post)
jim_clark_tools.gremove(term_to_post,"fin")
jim_clark_tools.gremove(term_to_post,"exam")

if do_fin:
    if not shutil.copy(FIN, fin_clean): #src, dest
        exit(0)
    clean_up_marks_file(fin_clean)

print("TERM grade statistics")
jim_clark_tools.gstats(term_to_post,width=6)

if do_fin:
    print("final grade statistics")
    jim_clark_tools.gstats(fin_clean,width=6)

from runit import runit
runit("ls -ltr %s %s %s %s" % (TERM, term_to_post))
if do_fin:
    runit("ls -ltr %s %s %s %s" % (FIN, fin_clean))

exit(0)    

