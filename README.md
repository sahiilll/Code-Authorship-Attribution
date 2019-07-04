# Code-Authorship-Attribution
The project aims to extract the features from the binary file with the purpose to form the classifiers with those features and determine the author of the binary file among the given dataset. It has been proven that stylistic features of the programmer stays even after the compilation in the executable binaries. 

We aim to first extract the features from the executable binaries. and then use a decompiler to decompile into a source code. For now we are only taking the C files. After the decompilation is done we are left with the source code in the files with extension ".cpp". 

##Source Code Analysis
###Abstract Syntax trees Extraction
For the lexical analysis, the above code uses the python binding of the clang library. Clang is a C language family front end for LLVM. In compiler design, a front end takes care of the analysis part, which means breaking up the source code into pieces according to a grammatical structure.

It parses the source code, checking it for errors and turning the input code into an Abstract Syntax Tree (AST). The latter is a structured representation, which can be used for different purposes such as creating a symbol table, performing type checking and finally generating code. The AST is the part I'm mainly interested in, as it is clang's core, where all the interesting stuff happens.

Using the clang, The code traverses through the abstract syntax trees and collects all the different type of nodes and tokens in the dictionary as its keys. The values of these depends on the type of measure. There are three type of values for now TF i.e. Term frequency (the ratio of the occurence of the keys(token + Node) in each file) and TFIDF(how much important is that token for the feature). For further reading refer, http://www.tfidf.com/

##Result
###Syntactical Features
With the help of the clang, we extracted all the features and saved it in a arff file along with the Tf and TFIDF values. ARFF stands for Attribute-Relation File Format. It is an ASCII text file that describes a list of instances sharing a set of attributes. ARFF files have two distinct sections. The first section is the Header information, which is followed by the Data information.
The Header of the ARFF file contains the name of the relation, a list of the attributes (the columns in the data), and their types.Feeding this output to the weka software we were able to get the accuracy of 57 percent without using Classification relaxationa and information gain. 

