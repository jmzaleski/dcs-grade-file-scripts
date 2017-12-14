import os

def runit_stdout_stderr(cmd,verbose=False,dry_run=False,debug=False):
    "utility function to run a command returns tuple of "
    def print_message(msg):
        if debug:
            print(msg) #i guess debug imples verbose
            input(" ...hit enter to continue..")
            return
        elif verbose:
            print(msg)
    print_message("about to run: %s" % cmd)
    # see https://stackoverflow.com/questions/31926470/run-command-and-get-its-stdout-stderr-separately-in-near-real-time-like-in-a-te
    if not dry_run:
        try:
            from subprocess import Popen, PIPE
            import traceback,sys
            with Popen(cmd, shell=True,stdout=PIPE, stderr=PIPE) as p:
                readable = {
                    p.stdout.fileno(): sys.stdout.buffer, # log separately
                    p.stderr.fileno(): sys.stderr.buffer,
                    }
                from select import select
                stdout_buf = ''
                stderr_buf = ''
                rc = 0
                while readable:
                    for fd in select(readable, [], [])[0]:
                        data = os.read(fd, 1024) # read available
                        if not data: # EOF
                            del readable[fd]
                        else:
                            #write out what the process writes on our own sys.stdout so we can see it
                            readable[fd].write(data) 
                            readable[fd].flush()
                            s = data.decode()
                            if fd == p.stdout.fileno():
                                stdout_buf += s
                            elif fd == p.stderr.fileno():
                                stderr_buf += s
                p.communicate()
                rc = p.returncode
                #print("stdout",stdout_buf)
                #print("stderr",stderr_buf)
                return (rc,stdout_buf,stderr_buf)
        except:
            traceback.print_exc(file=sys.stdout)
            print_message(cmd + " threw, exit 42")
            return (42,None,None)

def runit(cmd,verbose=False,dry_run=False,debug=False):
    "utility function to run a command"
    def print_message(msg):
        if debug:
            print(msg) #i guess debug imples verbose
            input(" ...hit enter to continue..")
            return
        elif verbose:
            print(msg)
    print_message("about to run: %s" % cmd)
    if not dry_run:
        try:
            rc = os.system(cmd)
        except:
            print_message(cmd + " threw, exit 42")
            return(42)
        if rc == 0:
            print_message("exited zero (clean) :") 
            return(0)
        else:
            print("%s exits %s non-zero dirty:" % (cmd,rc))
            return(rc)
        return(rc)
