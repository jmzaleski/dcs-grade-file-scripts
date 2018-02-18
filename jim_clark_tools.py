#!/opt/local/bin/python3.5

mark_dir = None
GBIN = None

from os import system
import sys
import os
import shutil
import itertools

#TODO: home dir

from runit import runit
from runit import runit_stdout_stderr
    
def gbin(exe):
    "utility function to encap location of grufty jim clarke grading program"
    if not os.path.isdir(os.path.join(mark_dir,GBIN)):
        print("cannot stat GRADE bin directory:", jim_clarke_grade_program_bin)
        exit(2)
    return os.path.join(mark_dir,GBIN,exe)

def gcopy(mark,SRC,DEST):
    "gcopy mark from grade file named SRC to grade file named DEST"
    cmd = "%s -m %s %s %s" % (gbin("gcopy"), mark, DEST, SRC)
    print("run", cmd)
    rc = runit(cmd) #,verbose=True,dry_run=False,debug=False)
    return(rc)

def gstats(fn,width=5):
    "run gstats on grade file called fn"
    runit( "%s -W %d %s" % (gbin("gstats"), width, fn))

def glint(fn):
    "run glint on grade file called fn"
    #runit( "%s %s" % (gbin("glint"), fn)) #stupid bloody glint doesn't exit non-zero on error!
    verbose = False
    cmd = "%s %s" % (gbin("glint"),fn)
    (rc,so,serr) = runit_stdout_stderr(cmd,verbose=verbose,dry_run=False,debug=False)
    if rc != 0:
        print(cmd, "glint returned non-zero???")
        return(rc)
    if len(so) > 0 or len(serr)>0:
        if verbose:
            print(cmd,"printed stuff, so given it's glint we're returning non-zero")
        return 42
    return 0
    
def gen(fn):
    "run gen on grades file called fn"
    runit( "%s %s" % (gbin("gen"), fn))

def gremove(fn,mark):
    "remove grade called mark from file fn"
    runit( "%s -c -m %s %s" % (gbin("gremove"), mark, fn))

def init(md,gbin):
    global mark_dir
    global GBIN
    mark_dir = md
    GBIN = gbin
    
if __name__ == '__main__':
    init(".","../../grades-bin/")
    glint("CSC2702HY-empty")
