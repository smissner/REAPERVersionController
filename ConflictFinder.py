#!/usr/bin/env python
# coding: utf-8

# In[9]:


import sys
try:
    fileLoc = sys.argv[1]
    file = open(fileLoc,"r")
except:
    print("Invalid file location")
lines = file.readlines()
conflictLines = []
ignorableConflicts = []
within = False
i = 0
sub = []
ignore = True
for l in lines:
    if("<PROJBAY" in l):
        ignore = False
    if("=======" in l or "<<<<<<<" in l):
        sub.append(i)
    if(">>>>>>>" in l):
        sub.append(i)
        if(ignore):
            ignorableConflicts.append(sub)
        else:
            conflictLines.append(sub)
        sub = []

    i += 1
print(ignorableConflicts)
print(conflictLines)

