#!/usr/bin/python

import os,re,sys
import csv

#######################################


#See http://texdoc.net/texmf-dist/doc/latex/geometry/geometry.pdf

latex_doc_header = r'''
\documentclass[16pt,english]{article}

\usepackage[T1]{fontenc}
\usepackage[latin9]{inputenc}
\usepackage[letterpaper,total={7in,8in},top=1.9in]{geometry}


\makeatletter

\renewcommand{\familydefault}{\sfdefault}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LyX specific LaTeX commands.
%% Because html converters don't know tabularnewline
\providecommand{\tabularnewline}{\\}

\usepackage{babel}
\begin{document}

%san serif
\sffamily

\part*{CSC302 P3 Demo Marking sheets. }

%latex generated by demo-marking-sheets.py
'''

# See http://tex.stackexchange.com/questions/10535/how-to-force-a-table-into-page-width

#######################################
latex_team_table = r'''
\begin{tabular*}{\textwidth}{|l @{\extracolsep{\fill}}|c|c|c|c|c|}
\hline 
\huge{Component} \hspace{2in} & \huge{0} & \huge{1} &  \huge{2} &  \huge{3} &  \huge{4}\tabularnewline
\hline 
\hline 
\huge{Clarity of Description of what was built}  &  &  &  &  & \tabularnewline
\hline 
\huge{Clarity of who users are} &  &  &  &  & \tabularnewline
\hline 
\huge{Clarity of why product is useful to users} &  &  &  &  & \tabularnewline
\hline 
\huge{Quality of Insights} &  &  &  &  & \tabularnewline
\hline 
\huge{Quality of Demo} &  &  &  &  & \tabularnewline
\hline 
\end{tabular*}
'''
#######################################
latex_indiv_table = r'''
\begin{tabular*}{\textwidth}{|l@{\extracolsep{\fill}}|l|l|c|c|c|c|c|}
\hline 
\huge{CDFID} & \huge{name} & \huge{githubid} & \huge{0} & \huge{1} &  \huge{2} &  \huge{3} &  \huge{4}\tabularnewline
\hline 
\hline 
'''
latex_row = r'''
\huge{%(cdfid)s} & %(name)s & \huge{%(githubid)s} &   &  &  & \tabularnewline
\hline 
'''
#######################################
latex_end_table = r'''
\end{tabular*}
'''
#######################################


def printTeamSection(num):
    #print r"{\setlength{\tabcolsep}{0.5em}"
    print r'''\part*{Team %s}''' % num
    print latex_team_table
    #print r"}" #end of setlength


def printIndivTable(cdfid_list,cdfid_map,github_map):
    print latex_indiv_table
    for cdfid in cdfid_list:
        name = ''
        if cdfid in cdfid_map:
            name = cdfid_map[cdfid]
        githubid = ''
        if cdfid in github_map:
            githubid = github_map[cdfid]
        print latex_row % {"cdfid": cdfid, "name": name, "githubid": githubid}
        print r"\cr\cr\hline\hline"

    print latex_end_table
    #print r"}" #end of setlength

def printIndivSection(cdfid_list,cdfid_map, github_map):
    print r"\part*{Individual Contributions}"
    printIndivTable(cdfid_list, cdfid_map, github_map)
    #print r"\newline"    
    #print r"\break"

# read group file (for cdfid's in groups)
import group_csv_file_reader
gfr = group_csv_file_reader.GroupFileReader("groups.csv")
groups = gfr.read_groups()

# read class list (for names)
import cdf_class_list_reader
cclr = cdf_class_list_reader.CdfClassListFileReader("CSC302H1S")
lines = cclr.readLines()
cdfid_to_name = cclr.cdfid_to_name(lines)

# read csv file mapping cdfid to github id
import map_file_reader
mfr = map_file_reader.MapFileReader("cdfid-to-githubid.csv",",")
cdfid_to_github = mfr.readMap()

# quick hack to print out tables in order groups are presenting
team_ids = groups.keys()
team_ids.sort()
team_order = ["T06", "T12", "T04", "T09", "T07", "T05", "T01", "T02", "T10", "T11", "T08", "T03"]
for t in team_order:
    if not t in team_ids:
        print t, "in team_order hacky list but not a key of groups hash"
        raise Exception("bad team name in team_order hack:"+t)

# generate the latex
print latex_doc_header 
for team_id in team_order:
    printTeamSection(team_id)
    printIndivSection(groups[team_id], cdfid_to_name, cdfid_to_github)
    print r"\clearpage"
print r"\end{document}"