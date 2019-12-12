import os, json 
from time import sleep
from os import system
import math
import copy
os.chdir("/home/sahil/Downloads/cuckoo/")
def getListOfFiles(dirName):
    #dirName = "/home/sahil/Downloads/cuckoo/"
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            if fullPath.endswith("ort.json"):
                allFiles.append(fullPath)   
    return allFiles

def collectapis(input_json):
    apis = {}
    try:
        apistats = input_json['behavior']['apistats']
        for procid, dic in apistats.items():
            for k,v in dic.items():
                apis[k] = v
    except:
        return apis
    return apis

def collectmodeules(input_json):
    modules = {}
    try:
        procs = input_json['behavior']['processes']
        for proc in procs:
            for k,v in proc.items():
                for i in proc['modules']:
                    for key, val in i.items():
                        if key == 'basename':
                            module = val.split("\\")[-1]
                        if module not in modules.keys():
                            modules[module] = 1
                        else:
                            modules[module] += 1
    except:
        return 
    return modules

def collectreg(input_json):
    regesteries = {}
    
    try:
        regs = input_json['behavior']['summary']['regkey_opened'] + \
        input_json['behavior']['summary']['regkey_written'] + \
        input_json['behavior']['summary']['regkey_read'] 
        for reg in regs:
            r  = reg.split("\\")[-1]
            if r not in regesteries.keys():
                regesteries[r] = 1
            else:
                regesteries[r] += 1
    except:
        return regesteries
    return regesteries
    
def collectmutexes(input_json):
    
    mutexes = {}
    try:

        muts = input_json['behavior']['summary']['mutex']
        for mut in muts:
            if mut not in mutexes.keys():
                mutexes[mut] = 1
            else:
                mutexes[mut] += 1
    except:
        return mutexes
    
    return mutexes

def collectstrings(input_json):
    
    strings = {}
    try:

        for st in input_json['strings']:
            if st not in strings.keys():
                strings[st] = 1
            else:
                strings[st] += 1
    except:
        return strings
    
    return strings  

def mergedic(d1, d2):
    d3 = {}
    for k,v in d1.items():
        d3[k] = v
    for k,v in d2.items():
        d3[k] = v
    return d3

def collectprivs(input_json):
  privs = {}
  l = []
  for i in input_json['memory']['privs']['data']:
      #st = str(i['filename']) + " : " + 
      st = str(i['description'])
      if st in  privs.keys():
          privs[st] += 1
      else:
          privs[st] = 1
        
  return privs

def calculatetf(beh, aall):
    finalTF = {}
    for fil,li in beh.items():
        types = []
        for feature in li:
            tot = sum(feature.values())
            TF = {}
            for name,freq in feature.items():
                tf = freq/tot
                TF[name] = tf
            types.append(TF)
        finalTF[fil] = types
    
    for li in range(len(aall)):
        for i in aall[li]:
            for fil in finalTF.keys():
                if i not in finalTF[fil][li].keys():
                    finalTF[fil][li][i] = 0
    return finalTF

def calculatetfidf(beh, aall, tf):
    
    finalTFIDF = {}
    idf = {}
    for j in aall:
        for i in j:
            idf[i] = 0
    N = len(beh.keys())
    for fil,li in beh.items():
        for i in li:
            for j in i.keys():
                idf[j] += 1
    
     
    for fil,li in beh.items():
        types = []
        for i in range(len(aall)):
            tfidf = {}
            for j in aall[i]:
                tfidf[j] = tf[fil][i][j] * math.log( 1 + N/idf[j],10)
            types.append(tfidf)
        finalTFIDF[fil] = types
    return finalTFIDF

def filterfeatures(beh, aall):
    idf = {}
    for i in aall:
        idf[i] = 0
    #N = len(beh.keys())
    for i in aall:
        for fil,li in beh.items():
            for l in li:
                if i in l.keys():
                    idf[i] += 1

    d = [ k for k,v in idf.items() if v > 1 ]
    return d

def filterstring(st):
    st = st.replace(",","")
    st = st.replace("[","")
    st = st.replace("]","")
    st = st.replace("'","")
    return st

def printarff(tf,tfidf):
    fi = open("ASTFeatures.arff","w")
    fi.write("@relation test\n")
    header = "@attribute instanceID_original {"
    for i in tf.keys():
        header = header + i.split("/")[-3] + ","
    header = header[0:len(header)-1] + "}"
    count = 0
    fi.write(header + "\n")
    
    for fil, li in tf.items():
        print(tf[fil][1])
        for i in range(len(li)):
            for k,v in li[i].items():
                k = filterstring(k)
                if i == 0:
                    str1 = "@attribute \'apiTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
            
                elif i == 1:
                    str1 = "@attribute \'modulesTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)

                elif i == 2:
                    str1 = "@attribute \'mutexesTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                
                elif i == 3:
                    str1 = "@attribute \'regsTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                elif i == 4:
                    str1 = "@attribute \'stringsTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                elif i == 5:
                    str1 = "@attribute \'privsTF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                
                count += 1
        break
    count = 0
    for fil, li in tf.items():
        for i in range(len(li)):
            for k,v in li[i].items():
                k = filterstring(k)
                if i == 0:
                    str1 = "@attribute \'apiTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)

                elif i == 1:
                    str1 = "@attribute \'modulesTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)

                elif i == 2:
                    str1 = "@attribute \'mutexesTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                
                elif i == 3:
                    str1 = "@attribute \'regsTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                elif i == 4:
                    str1 = "@attribute \'stringsTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)
                elif i == 5:
                    str1 = "@attribute \'privsTFIDF {}=[{}]\'".format(count,k) + " numeric" + "\n"
                    fi.write(str1)

                count +=1
        break
    footer = ""
    for f in tf.keys():
        footer = footer + f.split("/")[-4].replace(" ","") + ","
    footer = footer[0:len(footer)-1] 
    footer = ",".join(list(set(footer.split(","))))
    footer = "@attribute 'authorName_original' {" + footer + "}"
    fi.write(footer)
    fi.write("\n@data\n")
    
    for fil, li in tf.items():
        st = fil.split("/")[-3] + ","
        for i in range(len(li)):
            for k,v in li[i].items():
                st = st + repr(v) + ","
        for i in range(len(li)):
            for k,v in tfidf[fil][i].items():
                st = st + repr(v) + ","
        st = st + fil.split("/")[-4].replace(" ","")+"\n"

        fi.write(st)
               
if __name__=="__main__":

    exists = os.path.isfile('./ASTFeatures.arff')
    if exists:
        os.remove('./ASTFeatures.arff')


    dirName = "/home/sahil/Downloads/cuckoo/"
    reports = getListOfFiles(dirName)
    filenames= {} 
    reportdic = {}
    allapis = []
    allmodules = []
    allregs = []
    allmutexes = []
    allprivs = []
    allstrings = []
    behaviour = {}
    for rep in reports:

            try:
                results = {}
                jsonfile = open(rep, "r")
                data = json.load(jsonfile)

                apis = collectapis(data)
                allapis = list(set(apis.keys())) + allapis
                
                modules = collectmodeules(data)
                allmodules = list(set(modules.keys())) + allmodules
                
                mutexes = collectmutexes(data)
                allmutexes = list(set(mutexes.keys())) + allmutexes
                
                regs = collectreg(data)
                allregs = list(set(regs.keys())) + allregs 
                
                strings = collectstrings(data)
                allstrings = list(set(strings.keys())) + allstrings
                
                privs = collectprivs(data)
                allprivs = list(set(privs.keys())) + allprivs
    
                behaviour[rep] = [apis,modules,mutexes,regs,strings,privs]
    
            except Exception as e:
                print(e)

    #print(behaviour.keys())i
    allapis = filterfeatures(behaviour, allapis)
    allmodules = filterfeatures(behaviour, allmodules)
    allmutexes = filterfeatures(behaviour,allmutexes)
    allregs = filterfeatures(behaviour, allregs)
    allstrings = filterfeatures(behaviour, allstrings)
    allprivs = filterfeatures(behaviour, allprivs)
    

    aall = allapis + allmodules + allmutexes +  allregs +   allstrings + allprivs
    
    #fltering the keys in the filtered list of features
    for fil, li in behaviour.items():
        for i in range(len(li)):
            d = copy.deepcopy(li[i])
            for k,v in d.items():
                if k not in aall:
                    del behaviour[fil][i][k]
    aall = [allapis,allmodules,allmutexes,allregs,allstrings,allprivs]
    tf =  calculatetf(behaviour, aall)
    tfidf = calculatetfidf(behaviour, aall, tf)
    printarff(tf,tfidf)
