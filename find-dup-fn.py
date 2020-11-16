from __future__ import print_function  #allows print as function

import os
from os import system
from os import listdir

lightroom_folders="/Users/mzaleski/Pictures/lightroom-folders"
lightroom_collections="/Users/mzaleski/Pictures/lightroom-collections"

#rel_path="/tmp"
#if os.path.isfile(os.path.join(dir, f))]:
#    print(os.path.join(rel_path, fn))

#result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.txt']

lr_folder_dict = {}
lr_folder_size_dict = {}
folder_dups = []
for dp, dn, filenames in os.walk(lightroom_folders):
    #print("dir", dp)
    for f in filenames:
        #print("file:",f)
        if f in lr_folder_size_dict:
            if os.path.getsize(os.path.join(dp,f)) == lr_folder_size_dict[f]:
                if f in lr_folder_dict:
                    if False:print("duplicate file in folders??:", f, lr_folder_dict[f],dp)
                    lr_folder_dict[f].append(dp)
                    folder_dups.append(f)
        else:
            lr_folder_dict[f] = [dp]
            lr_folder_size_dict[f] = os.path.getsize(os.path.join(dp,f))

if False:            
    print("duplicate files in", lightroom_folders)
    for fn in folder_dups:
        for dir in lr_folder_dict[fn]:
            print(os.path.join(dir,fn),end=",")
        print("")
    exit(0)                  
    for fn in folder_dups:
        print(fn)

collection_dups = []
lr_collection_dict = {}
lr_collection_size_dict = {}

for dp, dn, filenames in os.walk(lightroom_collections):
    #print("dir", dp)
    for f in filenames:
        #print("file:",f)
        if f in lr_collection_dict and os.path.getsize(os.path.join(dp,f)) == lr_collection_size_dict[f]:
            #print("duplicate file found in collection:", f, lr_collection_dict[f],dp)
            lr_collection_dict[f].append(dp)
            collection_dups.append(f)
        else:
            lr_collection_size_dict[f] = os.path.getsize(os.path.join(dp,f))
            lr_collection_dict[f] = [dp]
if False:
    print("duplicate files in collections")
    for fn in collection_dups:
        for dir in lr_collection_dict[fn]:
            print(os.path.join(dir,fn),end=',')
        print("")
    
#print files that are in collections and in folders
for dp, dn, filenames in os.walk(lightroom_collections):
    #print("dir", dp)
    for fn in filenames:
        if fn in lr_folder_size_dict and fn in lr_collection_size_dict and lr_folder_size_dict[fn] == lr_collection_size_dict[fn]:
            #print  file in collection and then all dups in folders.
            print(os.path.join(dp,fn),end=",") 
            for d in lr_folder_dict[fn]:
                print(os.path.join(d,fn),end=",")
            print("")
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
