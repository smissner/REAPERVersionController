#!/usr/bin/env python
# coding: utf-8

# In[7]:


from ConflictFinder import ConflictFinder
import sys
fileLoc = sys.argv[1]
names = ConflictFinder.nameConflicts(fileLoc)
for name in names[:-1]:
    print(name + ",")
print(names[len(names) - 1])

