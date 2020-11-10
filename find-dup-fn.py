from __future__ import print_function  #allows print as function

import os
from os import system
from os import listdir

root="/Users/mzaleski/Pictures/"
rel_path="/tmp"
#if os.path.isfile(os.path.join(dir, f))]:
#    print(os.path.join(rel_path, fn))

#result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.txt']

fn_dict = {}
dups = []
for dp, dn, filenames in os.walk(root):
    #print("dir", dp)
    for f in filenames:
        #print("file:",f)
        if f in fn_dict:
            #print("duplicate file:", f, fn_dict[f],dp)
            fn_dict[f].append(dp)
            dups.append(f)
        else:
            fn_dict[f] = [dp]
print("duplicate files")
for fn in dups:
    print(fn, fn_dict[fn])
exit(0)        

# for dir in os.listdir(root):
#     if os.path.isfile(dir):
#         print("file:",dir)
#     elif os.path.isdir(dir):
#         print("dir:",dir)
#         for fn in os.listdir(dir):
#             print(dir,fn)
#     else:
#         print("what is dir??", dir)
    
# exit(0)
# for fn in [f for f in os.listdir(dir)]:
#     print(fno)
