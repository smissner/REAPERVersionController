#!/usr/bin/env python
# coding: utf-8

# In[13]:


from nostril import nonsense
import os
class ConflictFinder:
    def createConflicts(f1:str,f2:str,newfilename = "",newloc = "."):
        if(newfilename == ""):
            newfilename = f1 + "compare" + f2
        os.system("fc " + f1 + " " + f2 + " >> comparefilef3.txt")
        conlines = ConflictFinder.getLines("./comparefilef3.txt")
        flines = ConflictFinder.getLines(f1)
        f = open(newloc + "/" + newfilename,"w")
        j = 1
        i = 0
        findline = ""
        while(i<len(flines)):
            line = flines[i]
            while((findline == "" or findline == "\n") and j < len(conlines)):
                if("*****" not in conlines[j] and conlines[j] != "\n"):
                    findline = conlines[j]
                else:
                    j += 1
            if(line == findline):
                f.write(line)
                if("<REAPER_PROJECT" not in findline):
                    f.write("<<<<<<< " + f1 + "\n")
                    check = True
                    nlines = []
                    while(conlines[j] != "*****\n"):
                        j += 1
                        if("*****" in conlines[j]):
                            if(conlines[j] != "*****\n"):
                                nlines.pop()
                                nlines.append("=======\n")
                                check = False
                                j += 1
                            else:
                                nlines.pop()
                                nlines.append(">>>>>>>" + f2 + "\n")
                                for nl in nlines:
                                    f.write(nl)
                        else:
                            nlines.append(conlines[j])
                        if(check):
                            i += 1
                else:
                    while(conlines[j] != "*****\n"):
                        j += 1
                findline = ""
            else:
                f.write(line)
            
            i += 1
        os.remove("./comparefilef3.txt")
        f.close()
            
        
    def findConflicts(fileLoc:str):        
        lines = ConflictFinder.getLines(fileLoc)
        conflictLines = []
        ignorableConflicts = []
        within = False
        i = 0
        sub = []
        ignore = True
        for l in lines:
            if("GLOBAL_AUTO" in l):
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
            while(i>=0 and "GLOBAL_AUTO" not in lines[i]):
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
            if(name[0] == ":"):
                name = name[1:]
            names.append(name.replace("\n",""))
        return names
            
            
            
    def getLines(fileLoc:str):
        try:
            file = open(fileLoc,"r")
        except:
            print("Invalid file location")
        return file.readlines()

