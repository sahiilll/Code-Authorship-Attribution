#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import clang.cindex
import os
import math
import re

Cfiles = []
rese = dict()
TF = dict()
TFIDF = dict()
IDF = dict()
incl = dict()
Regex_pattern = r"^//." # for single line comments 
Regex_pattern2 = r"/\*.*?\*/" # for single slash-star line comments
Regex_pattern3 = r'\"(.+?)\"' # for double quoted strings 
Regex_pattern4 = r'\/\*(.|[\r\n])*\*\/' # multiline slash-star comments
# Tell clang.cindex where libclang.dylib is
#clang.cindex.Config.set_library_path("/usr/lib/llvm-6.0/lib")
#index = clang.cindex.Index.create()



# to find the difference of values between the output of joern and clang
def diffbet():
        print("These are the tokens which are present in clang but not in Joern AST")
        s = set(rese.keys())
        for i in tokendic.keys():
                if i not in s:
                        print(i)

        print("These are the tokens which are present in joern but not in clang")
        count = 0
        s = set(tokendic.keys())
        for i in rese.keys():
                if i not in s:
                        print(i)
                        count+=1
        print(count)

# code snippet to read the arff file
def readarff():

        Regex_pattern4 = r"(?<=\[)(.*?)(?=\])" # for filtering the tokens from arff file

        f = open("/home/kejsi/research/arffs/ASTFeatures.arff", "r")

        for i in f.readlines():
                result = re.search(Regex_pattern4, i)
                #print((i.split('['))[1].split(']')[0])
                if result:
                        rese[result.group(1)] = 0
fuck = dict()
# Traverse the AST tree
def checksource(node):

        if node.location.file == None:
                #print(node.displayname)
                return True
        elif str(node.location.file.name) in Cfiles:
                return True
        else:
                return False

def traversetokens(node):
	global tokendic
	global stats

	for child in node.get_children():
		if checksource(child):
			traversetokens(child)

	for token in node.get_tokens():
		if not ((bool(re.search(Regex_pattern2, token.spelling))) \
			or (bool(re.search(Regex_pattern, token.spelling))) \
			or (token.spelling == "}")
			or (token.spelling == "{")
			or (bool(re.search(Regex_pattern4, token.spelling)))):
                        #or (bool(re.search(Regex_pattern3, token.spelling)))):     #uncomment it if you want strings to be filtere
			t = token.spelling
			if ifinteger(str(t)):
				t = "number"
			if ifhex(str(t)):
				t = "hex"
			if t.startswith("\'"):
				#print(t)
				t = t.replace("'", "")
				#print(t)
			if t not in tokendic.keys():
				tokendic[t] = 1
			else:
				tokendic[t] +=1

		if not node.kind.name in stats.keys():
                	stats[node.kind.name] = 1
		else:
			stats[node.kind.name]= stats[node.kind.name] + 1

#Helper function to check if string is integer or not
def ifinteger(s):
        if s[0] in ('-', '+'):
                return s[1:].isdigit()
        return s.isdigit()

#Helper Function to check if teh token is  hexadecimal number
def ifhex(s):
        if s.startswith('0x'):
                try:
                        value = int(s,16)
                        return True
                except:
                        return False
        else:
                return False

def readpaths():
#Print all the paths that contain *.cpp extensions
        global Cfiles 
        for root, dirs, files in os.walk("/home/sahil/3authors"):
                for file in files:
                        if file.endswith(".cpp"):
                                Cfiles.append(os.path.join(root, file))

def printtokens():
        for i in tokendic.keys():
                print("{} :::: {}".format(i, tokendic[i]))
        print("Total Number of Unique tokens :", len(tokendic.keys()))
        print("Total Number of tokens found in all files: ",sum(tokendic.values()))

def calculatetf(dictionary,stats,f):
        #print(dictionary.values())
        tf = dict()
        tot = sum(dictionary.values())
        #print(tot)
        for i in dictionary.keys():
                tf[i] = float(float(dictionary[i])/float(tot))

        tot = sum(stats.values())
        for i in stats.keys():
                tf[i]=stats[i]/tot

        TF[f] = tf
        #print(TF[f].values())


def calculateidf(dictionary, stats):
	for i in dictionary:
		if i in IDF.keys():
			IDF[i]+=1
		else:
			IDF[i]=1

	for i in stats.keys():
		if i in IDF.keys():
			IDF[i]+=1
		else:
			IDF[i]=1

def calculatetfidf(f):
        global total_number_documents
        tfidf = dict()
        for i in TF[f].keys():
                k = math.log(total_number_documents/IDF[i])

                tfidf[i] = TF[f][i]*k

        TFIDF[f]=tfidf 



def printresult():
        for f in Cfiles:
                print("-----------------------------------------------------------------------------------------------------")
                print(f)
                print("-----------------------------------------------------------------------------------------------------")
                for i in TF[f].keys():
#                       print("TF of {} token is : {}".format(i,TF[f][i]))
                        print("TFIDF of {} token is : {}".format(i, TFIDF[f][i]))

def printarffs():
    fi = open("ASTFeatures.arff","w")
    fi.write("@relation test\n")
    header = "@attribute instanceID_original {"
    for f in Cfiles:
        header = header + f.split("/")[-1].split("hexrays_decompiled")[0] + "," 
    header = header + "}"
    count = 0
    fi.write(header + "\n")
    #str2 = f.split("/")[-1].split("hexrays_decompiled")[0] + ","
    f = Cfiles[0]
    for i in TF[f]:
        str1 = "@attribute \'ASTNodeTypesTF {}=[{}]\'".format(count,i) + " numeric" +"\n"
        fi.write(str1)
        count+=1
    count=0
    for i in TF[f]:
        str1 = "@attribute \'ASTNodeTypesTFIDF {}=[{}]\'".format(count,i) + " numeric" +"\n"
        fi.write(str1)
        count+=1
    footer = ""
    for f in Cfiles:
                        footer = footer + f.split("/")[4] + " "
    footer = ",".join(list(set(footer.split(" "))))
    
    footer = "@attribute 'authorName_original' {" + footer + "}"
    
    fi.write(footer)
    fi.write("\n@data\n")
    for f in Cfiles:
        fi.write(f.split("/")[-1].split("hexrays_decompiled")[0] + ",")
        for i in TF[f]:
            v = TF[f][i]
            fi.write(repr(v) + ",")
        for i in TFIDF[f]:
            v = TFIDF[f][i]
            fi.write(repr(v) + ",")
        fi.write(f.split("/")[4] + "\n")



def listofincludes(root_node):
        inc = dict()
        for included in root_node.get_includes():
                inc[str(included.include)] = None
        return inc

def unitekeys():
        A = set()
        for f in Cfiles:
                A = A | set(TF[f].keys())
        for f in Cfiles:
                for i in A:
                        if i not in TF[f].keys():
                                TF[f][i] = 0.0
                                TFIDF[f][i] = 0.0 

if __name__ == "__main__":

        #First extract and save all the paths for .cpp files in an array
        readpaths()

        total_number_documents = len(Cfiles)

        #Check if output file exists or not. If exists delete it
        exists = os.path.isfile('./ASTFeatures.arff')
        if exists:
                os.remove('./ASTFeatures.arff')

        # Tell clang.cindex where libclang.dylib is
        clang.cindex.Config.set_library_path("/usr/lib/llvm-6.0/lib")
        index = clang.cindex.Index.create()

        # Generate AST from every filepath f with extention cpp
        for f in Cfiles:

                tu = index.parse(f)
                root = tu.cursor  # Get the root of the AST
                #incl = listofincludes(tu)
                tokendic = dict()
                stats =dict()
                traversetokens(root)
                calculateidf(tokendic,stats)
                calculatetf(tokendic,stats,f)

        for f in Cfiles:
                calculatetfidf(f)
        unitekeys()
        printarffs()
