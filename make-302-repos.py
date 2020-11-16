from __future__ import print_function  #allows print as function
import csv, sys

# CSC302: print out yaml appropriate for gitomator to create team repos and populate
# collaborators with the teams

# input from two csv files:
# TODO: do the parseargs thing

# 1. csv file listing group name and **utorid** of eack member of each group
# (exported from google "signup sheet" publically writable by class)

FN="csc302-2020F-P0-project-team-formation-signup-sheet - by-utorid.csv"

# 2. csv file mapping utorid's to githubid (typically gathered from google form)
# (exported as CSV from google form responses  filled out by class in early days of semester)
MN="CSC302H1F-2020-Initial-Username-Registration (Responses) - Form Responses 1.csv"

# small classes have just one TA
#TA = ['MusaTalluzi']
TA = []  #covidized.. 0 TAs!

utorid_to_github_map = {}

def repo_name(gn):
    "concoct a name for the project repo by mangling group name"
    return "proj-%s" % gn

def individual_repo_name(utorid):
    "concoct a name for the repo by mangling utorid name"
    return "a3-%s" % utorid

# boilerplate header of gitomator input file
YAML_HDR = '''
default_access_permission: write

repo_properties:
  description: "initally empty repo, intended for csc302 project, created by make-302-repos.py"
  private: true

repos:
'''

# one of the things you can put in the yaml file is the repo
# read/write permission each member of the group will have for the
# newly created repo

def print_gitomator_yaml(list_of_lists,TA):
    # printout the yaml for gitomator
    print(YAML_HDR)
    for l in list_of_lists:
        group_name = l.pop(0)
        #print("ta",ta,"group_name",group_name)
        print("  - %s: " % repo_name(group_name))
        
        #16 magic number to align : in a col. much easier to proof
        fmt = "    - %-16s : write" 
        for utorid in l[0]:
            if len(utorid) == 0:
                continue
            if not utorid in utorid_to_github_map:
                print('skip',utorid, "because not in utorid_to_github_map",file=sys.stderr)
                continue
            github_id = utorid_to_github_map[utorid]
            print(  fmt % github_id )
        for ta in TA:
            print(  fmt % ta )
        print("") 

def print_gitomator_individual_yaml(list_of_lists,TA):
    # printout the yaml for gitomator for each students individual repo
    print(YAML_HDR)
    for l in list_of_lists:
        group_name = l.pop(0) #junk
        # 16 magic number to align : in a col. much easier to proof
        fmt = "    - %-16s : write" 
        for utorid in l[0]:
            if len(utorid) == 0:
                continue #no utorid? no repo
            if not utorid in utorid_to_github_map:
                print('skip',utorid,"because not in utorid_to_github map", file=sys.stderr)
                continue
            github_id = utorid_to_github_map[utorid]
            print("  - %s: " % individual_repo_name(utorid))
            print(  fmt % github_id )
            for ta in TA:
                print(  fmt % ta )
                print("\n") 
        
def sanity_check(list_of_lists):
    # check the inputs
    print("sanity check team utorid list of lists")
    for l in list_of_lists:
        group_name = l.pop(0)
        print("sanity checking team", repo_name(group_name),"...")
        
        for utorid in l[0]:
            if len(utorid) == 0:
                #print('will skip empty utorid', file=sys.stderr)
                continue
            if not utorid in utorid_to_github_map:
                print(utorid, 'not in utorid to github map', file=sys.stderr)
                continue

if __name__ == "__main__" :
    import csv

    is_hdr = True
    # read the utorid to github map file and create utorid_to_github_map
    with open(MN, 'r') as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',')
        if is_hdr:
            next(csv_file_reader)
        for x in csv_file_reader:
            utorid = x[2]
            githubid = x[3].replace("https://github.com/","")
            utorid_to_github_map[utorid] = githubid
    #print(utorid_to_github_map)

    list_of_lists = []
    # read the (utorid) team file into a list of lists
    with open(FN, 'r') as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',')
        if is_hdr:
            next(csv_file_reader)
        for group_list in csv_file_reader:
            #skip empty lines
            if len(group_list[0]) == 0:
                continue
            group_name = group_list[0]
            if group_name == "Cute Team Name":
                print("ignoring Cute Team Name")
                continue
            utorids = group_list[1:]
            #print(group_name, utorids)
            l = [group_name]
            l.append(utorids)
            #print(l)
            #list_of_lists.append(group_list)
            list_of_lists.append(l)
    # sometimes there is a line of column headers in the CSV file
    if False:
        header = list_of_lists.pop(0)
        #print("header:", list_of_lists.pop(0) )

    #print(TA)
    if True:
        #team repos
        print_gitomator_yaml(list_of_lists,TA)
    else:
        #a3 repos
        #sanity_check(list_of_lists)
        print_gitomator_individual_yaml(list_of_lists,TA)
        
    exit(0)

    
