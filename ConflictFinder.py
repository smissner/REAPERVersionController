#!/usr/bin/env python
# coding: utf-8

# In[39]:


from nostril import nonsense
class ConflictFinder:
    def findConflicts(fileLoc:str):        
        lines = ConflictFinder.getLines(fileLoc)
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
        return [ignorableConflicts,conflictLines]
    def nameConflicts(fileLoc:str):
        conflictLines = ConflictFinder.findConflicts(fileLoc)[1]
        lines = ConflictFinder.getLines(fileLoc)
        names = []
        for c in conflictLines:
            iInfo = lines[c[0] + 1]
            fChar = next(i for i, j in enumerate(iInfo) if j.strip())
            try:
                name = ":" + iInfo[fChar:iInfo.index(" ",fChar)]
            except:
                name = ":" +  iInfo[fChar:]
            try:
                if(nonsense(name)):
                    name = ""
            except:
                pass
            i = c[0] - 1
            closed = False
            while(i>=0 and "<PROJBAY" not in lines[i]):
                line = lines[i]
                if("NAME" in line):
                    try:
                        name = line[line.index("NAME") + 5:] + name
                    except:
                        pass
                    i = -1
                    continue
                fChar = next(i for i, j in enumerate(line) if j.strip())
                if(line[fChar] == "<"):
                    if(closed):
                        closed = False
                    else:
                        try:
                            spaceC = 0
                            stat = ""
                            for x in line[fChar + 1:]:
                                if(x == " "):
                                    spaceC += 1
                                    if(spaceC>=2):
                                        break
                                stat = stat + x
                            name = name + ":" + stat
                        except:
                            pass
                if(line[fChar] == ">"):
                    closed = True
                i = i - 1
            names.append(name.replace("\n",""))
        return names
            
            
            
    def getLines(fileLoc:str):
        try:
            file = open(fileLoc,"r")
        except:
            print("Invalid file location")
        return file.readlines()

