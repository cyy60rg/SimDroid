# This file is part of Elsim
#
# Copyright (C) 2012, Anthony Desnos <desnos at t0t0.fr>
# All rights reserved.
#
# Elsim is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Elsim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Elsim.  If not, see <http://www.gnu.org/licenses/>.

import logging

#--------- # hashlib is for finding the hash of the method sig. analysis class is imported to find the signature for finding similar method

import sys,hashlib
from androguard.core.analysis import analysis
DEFAULT_SIGNATURE = analysis.SIGNATURE_L0_4

#--------- 

ELSIM_VERSION = 0.2

log_elsim = logging.getLogger("elsim")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
log_elsim.addHandler(console_handler)
log_runtime = logging.getLogger("elsim.runtime")          # logs at runtime
log_interactive = logging.getLogger("elsim.interactive")  # logs in interactive functions
log_loading = logging.getLogger("elsim.loading")          # logs when loading

def set_debug() :
    log_elsim.setLevel( logging.DEBUG )

def get_debug() :
    return log_elsim.getEffectiveLevel() == logging.DEBUG

def warning(x):
    log_runtime.warning(x)

def error(x) :
    log_runtime.error(x)
    raise()

def debug(x) :
    log_runtime.debug(x)

#-------------- Function to find the match between classes
def find_match(nl11,nl12,nl13,nl21,nl22,nl23,m,f,u):
    if ((m > 0.0 and m < 50.0) or (f > 0.0 and f < 50.0) or (u > 0.0 and u < 50.0)):
	return 0
    elif m == 0.0:
	if nl11 > 0 or nl21 > 0:
	    return 0
    elif f == 0.0:
	if nl12 > 0 or nl22 > 0:
	    return 0
    elif u == 0.0:
	if nl13 > 0 or nl23 > 0:
	    return 0
    return 1
#-----------------	
		 	
     	

from similarity.similarity import *

FILTER_ELEMENT_METH         =       "FILTER_ELEMENT_METH"
FILTER_CHECKSUM_METH        =       "FILTER_CHECKSUM_METH"      # function to checksum an element
FILTER_SIM_METH             =       "FILTER_SIM_METH"           # function to calculate the similarity between two elements
FILTER_SORT_METH            =       "FILTER_SORT_METH"          # function to sort all similar elements 
FILTER_SORT_VALUE           =       "FILTER_SORT_VALUE"         # value which used in the sort method to eliminate not interesting comparisons 
FILTER_SKIPPED_METH         =       "FILTER_SKIPPED_METH"       # object to skip elements
FILTER_SIM_VALUE_METH       =       "FILTER_SIM_VALUE_METH"     # function to modify values of the similarity

BASE                        =       "base"
ELEMENTS                    =       "elements"
HASHSUM                     =       "hashsum"
SIMILAR_ELEMENTS            =       "similar_elements"
HASHSUM_SIMILAR_ELEMENTS    =       "hash_similar_elements"
NEW_ELEMENTS                =       "newelements"
HASHSUM_NEW_ELEMENTS        =       "hash_new_elements"
DELETED_ELEMENTS            =       "deletedelements"
IDENTICAL_ELEMENTS          =       "identicalelements"
INTERNAL_IDENTICAL_ELEMENTS =       "internal identical elements"
SKIPPED_ELEMENTS            =       "skippedelements"
SIMILARITY_ELEMENTS         =       "similarity_elements"
SIMILARITY_SORT_ELEMENTS    =       "similarity_sort_elements"


class ElsimNeighbors :
    def __init__(self, x, ys) :
        import numpy as np
        from sklearn.neighbors import NearestNeighbors
        #print x, ys

        CI = np.array( [x.checksum.get_signature_entropy(), x.checksum.get_entropy()] )
        #print CI, x.get_info()
        #print

        for i in ys : 
            CI = np.vstack( (CI, [i.checksum.get_signature_entropy(), i.checksum.get_entropy()]) )

        #idx = 0
        #for i in np.array(CI)[1:] :
        #    print idx+1, i, ys[idx].get_info()
        #    idx += 1

        self.neigh = NearestNeighbors(2, 0.4)
        self.neigh.fit(np.array(CI))
        #print self.neigh.kneighbors( CI[0], len(CI) )

        self.CI = CI
        self.ys = ys

    def cmp_elements(self) :
        z = self.neigh.kneighbors( self.CI[0], 5 )
        l = []
        
        cmp_values = z[0][0]
        cmp_elements = z[1][0]
        idx = 1
        for i in cmp_elements[1:] :
            
            #if cmp_values[idx] > 1.0 :
            #    break

            #print i, cmp_values[idx], self.ys[ i - 1 ].get_info()
            l.append( self.ys[ i - 1 ] )
            idx += 1

        return l

def split_elements(el, els) :
    e1 = {}
    for i in els :
        e1[ i ] = el.get_associated_element( i )
    return e1

####
# elements : entropy raw, hash, signature
# 
# set elements : hash
# hash table elements : hash --> element

#-----------###A function to find the match percent between 2 lists
def get_list_match(l1,l2,file_d1=None):
    n=0
    nl1=len(l1)
    nl2=len(l2)
    	
    if nl1==0 or nl2==0:
	return 0
    #file_d1.write(str(l1))
    #file_d1.write("\n")
    #file_d1.write(str(l2))
    #file_d1.write("\n")		
    for i in range(0,len(l2)):
        for j in range(0,len(l1)):
     	    if l2[i]==l1[j]:
        	n+=1
            	l1.pop(j)
            	break
    #file_d1.write(str(n))
    #file_d1.write("\n")	
    #return n	
    return ((float(2*n)/float(nl1+nl2))*float(100))
#-------------

class Elsim :
    def __init__(self, e1, e2, F, T=None, C=None, libnative=True, libpath="elsim/elsim/similarity/libsimilarity/libsimilarity.so") :
        self.e1 = e1
        self.e2 = e2
        self.F = F
        self.compressor = BZ2_COMPRESS#SNAPPY_COMPRESS
#----------
	#print "Checking e!!"
	#print self.e1
	#print self.e2
	#print self.e1.vm
#-----------
        set_debug()

        if T != None :
            self.F[ FILTER_SORT_VALUE ] = T

        if isinstance(libnative, str) :
            libpath = libnative
            libnative = True

        self.sim = SIMILARITY( libpath, libnative )

        if C != None :
            if C in H_COMPRESSOR :
                self.compressor = H_COMPRESSOR[ C ]

            self.sim.set_compress_type( self.compressor )
        else :
            self.sim.set_compress_type( self.compressor )

        self.filters = {}

        self._init_filters()
        self._init_index_elements()
#-----------
	self.classes_list=[]
	#file_d=open('../Analysis_androgd/classes.txt','w')  # File contains list of classes 
	#self.classes=self.e1.vm.get_classes_def_item() # returns an object of classDefItem of apk1 
	#file_d.write(str(self.classes.get_names()))
	#file_d.write("\n2nd\n")
	#self.classes=self.e2.vm.get_classes_def_item()
	#file_d.write(str(self.classes.get_names()))
	#file_d.write("\n")
	#file_d.close()

	self._init_same_classes()
	self.sim_analysis()
#-----------
        #self._init_similarity()
        #self._init_sort_elements()
        #self._init_new_elements()

    def _init_filters(self) : # function to initialize the list
#--------->>
	#file_d=open('../Analysis_androgd/method_sig.txt','w') # File contains method signature (used for finding similar methods)
	#file_d.close()	
	#file_d=open('/home/exodus/Phone_APKs/elements.txt','w')
	self.data_list_cls={}
	self.methd_hash_list={}
	self.match_classes={}
#----------
        #self.filters = {}
        #self.filters[ BASE ]                = {}
        #self.filters[ BASE ].update( self.F )
	
	#print self.filters[BASE]
        
	#self.filters[ ELEMENTS ]            = {}
        #self.filters[ HASHSUM ]             = {}
        #self.filters[ IDENTICAL_ELEMENTS ]  = set()
	
	#print self.filters[IDENTICAL_ELEMENTS]

	#self.filters[ SIMILAR_ELEMENTS ]    = []
        #self.filters[ HASHSUM_SIMILAR_ELEMENTS ]    = []
        #self.filters[ NEW_ELEMENTS ]        = set()
        #self.filters[ HASHSUM_NEW_ELEMENTS ]        = []
        #self.filters[ DELETED_ELEMENTS ]    = []
        #self.filters[ SKIPPED_ELEMENTS ]     = []

        #self.filters[ ELEMENTS ][ self.e1 ] = []
        #self.filters[ HASHSUM ][ self.e1 ]  = []

        #print self.filters

        #self.filters[ ELEMENTS ][ self.e2 ] = []
        #self.filters[ HASHSUM ][ self.e2 ]  = []
#--------->>	        
        #file_d.write(str(self.filters[ELEMENTS ]))
	#file_d.write("\n")
	#file_d.write(str(self.filters[ELEMENTS ]))
	#file_d.write("\n")
	#file_d.close()
#--------->>		
        #self.filters[ SIMILARITY_ELEMENTS ] = {}
        #self.filters[ SIMILARITY_SORT_ELEMENTS ] = {}
	#print self.filters
        #self.set_els = {}
        #self.ref_set_els = {}
        #self.ref_set_ident = {}

    def _init_index_elements(self) :
        self.__init_index_elements( self.e1, 1 )
        self.__init_index_elements( self.e2 )


    def __init_index_elements(self, ce, init=0) : # initialize for both apk1 and apk2 (0 for apk1)
        #self.set_els[ ce ] = set()
	#self.ref_set_els[ ce ] = {}
        #self.ref_set_ident[ce] = {}
#---------->>	
	self.data_list_cls[ce]=[] # conatins classes of each apk
	self.methd_hash_list[ce]={}  # contains methods and its hash for each apk

        
	#if init==1:
	    #file_d=open('../Analysis_androgd/elements1.txt','w') # Contains classes 
	    #file_d1=open('../Analysis_androgd/methd1.txt','w') # contains method details and hash (class name, method name, method hash)
	    #file_d2=open('../Analysis_androgd/method1.txt','w')	# contains method details like (class name, method name, method descriptor, method object reference, signature(opcode sequence + method descriptor))  	
	#else:
	    #file_d=open('../Analysis_androgd/elements2.txt','w') #same as above (for apk2)
	    #file_d1=open('../Analysis_androgd/methd2.txt','w')
	    #file_d2=open('../Analysis_androgd/method2.txt','w')
	#for i in ce.get_classes():
	    #str1=i.get_name()
	    #str1+="\n"
	    #file_d.write(str1)	
	#file_d.write("cls\n")
	n_classes=0
	n_methods_apk=0
	for i in ce.get_classes() :
	    n_classes+=1	
	    if i not in self.data_list_cls[ce]:
		self.data_list_cls[ce].append(i)
		methd_list=i.cls_methd_ref
		for j in methd_list:
		    n_methods_apk+=1
		    if j not in self.methd_hash_list[ce]:
			#self.methd_hash_list[ce].append(j)
			self.methd_hash_list[ce][j]=[]
			self.methd_hash_list[ce][j].append(hashlib.sha256(j.get_methd_sig().encode('ascii','ignore')).hexdigest())
			#file_d1.write("%s %s : %s : %s\n"%(j.get_class_name(),j.get_name(),self.methd_hash_list[ce][j],j))
			#file_d2.write("%s %s %s : %s : \n%s\n"%(j.get_class_name(),j.get_name(),j.get_descriptor(),j,j.get_methd_sig()))
	#file_d1.write("\nNo: of classes: %d\n No: of methods: %d"%(n_classes,n_methods_apk))		
	if init==1:
	    for i in ce.get_classes() :
		self.match_classes[i]=[]	
	    #file_d.write("Match")
	    #file_d.write(str(self.match_classes))
	        
	#for i in self.data_list_cls[ce]:
	    #str1=str(i)
	    #str1+=": "
	    #str1+=i.get_name()
	    #str1+="\n"
	    #str1+=str(sys.getsizeof(i))
	    #file_d.write(str1)
	#file_d.write("cls2\n")
#----------!!
   
        #for ae in ce.get_elements() :
	    #e = self.filters[BASE][FILTER_ELEMENT_METH]( ae, ce )	# e - is a intance of the class 'Method' in elsim_dalvik.py 
	    
	    #print "ae-en"	
	    #print ae
            #print self.filters

            #if self.filters[BASE][FILTER_SKIPPED_METH].skip( e ) :
                #self.filters[ SKIPPED_ELEMENTS ].append( e )
                #continue
            
            #self.filters[ ELEMENTS ][ ce ].append( e )
            #fm = self.filters[ BASE ][ FILTER_CHECKSUM_METH ]( e, self.sim )	# fm - is a instance of class 'CheckSumMeth' which creates signature of a method in the apk file and hash is calculated
            #e.set_checksum( fm )

#------------
            #file_d.write(e.get_info())
            #file_d.write("\n")
#-------------
            #sha256 = e.getsha256()
#--------------
	    #print init
	    #print e
	    #print sha256
	
            #self.filters[ HASHSUM ][ ce ].append( sha256 )
            #print "hash123"
	    #print "%s: %s" %(e,sha256)
            #if sha256 not in self.set_els[ ce ] :
                #self.set_els[ ce ].add( sha256 )
                #self.ref_set_els[ ce ][ sha256 ] = e
                
                #self.ref_set_ident[ce][sha256] = []
            #self.ref_set_ident[ce][sha256].append(e)
#---------	
	#print self.set_els
	#print "toto"
	#print self.filters

	#file_d.close()
	#file_d1.close()
#---------
#------------->>
    def _init_same_classes(self): #Function to find classes with same birthmark
	flag=0
	#file_d=open('../Analysis_androgd/match.txt','w') # birthmark match value of each classes 
	#file_d1=open('../Analysis_androgd/Check.txt','w') # Just for checking of birthmark matching (no need to uncomment)
	file_d2=open('../Analysis_androgd/perfect_match.txt','w') # Similar classes based on threshold with match percent (50 %)
	file_d3=open('../Analysis_androgd/class_birthmark.txt','w') # list of classes and its matching classes
	#file_d4=open('../Analysis_androgd/ident_func.txt','w') # Only contains classes and its corresponding function (not needed )
	#file_d5=open('../Analysis_androgd/sim_func.txt','w')
	for i in self.data_list_cls[self.e1]:
	    l11=i.cls_methd
	    l12=i.cls_field_var
	    l13=i.cls_used_cls	
	    if len(l11)!=0 or len(l12)!=0 or len(l13)!=0:
		for j in self.data_list_cls[self.e2]:
		    #file_d1.write("Class: %s : %s\n"%(i.get_name(),j.get_name()))
		    
		    l21=j.cls_methd
		    l22=j.cls_field_var
		    l23=j.cls_used_cls
#----The original func call is the 2nd call
		    methd=get_list_match(l11[:],l21[:])	
		    #methd=get_list_match(l11[:],l21[:],file_d1)				# The copy of the list is being passed to the function using [:] otherwise a reference is being passed so any operation to list in the function will reflect to the original function
		    #if methd>=1:
			#file_d.write("checking\n%s %s\n"%(i.cls_methd,methd))
#----The original func call is the 2nd call
		    fld=get_list_match(l12[:],l22[:])
		    usd_cls=get_list_match(l13[:],l23[:])
	
		    #fld=get_list_match(l12[:],l22[:],file_d1)
		    #usd_cls=get_list_match(l13[:],l23[:],file_d1)


		    str1="(%s,%s) : (%s,%s)\n" %(str(i),i.get_name(),str(j),j.get_name())
		    str1+="\t Method match: %f\t Field match: %f\t Used Class match: %f\n" %(methd,fld,usd_cls)
		    #file_d.write(str1)
		    if usd_cls >=50.0 or fld >=50.0 or methd >=50.0:
			file_d2.write(str1.encode('utf-8'))
			flag=find_match(len(l11),len(l12),len(l13),len(l21),len(l22),len(l23),methd,fld,usd_cls)
			file_d2.write("flag: %s\n"%(flag))
			if flag==1:
			    if j not in self.match_classes[i]:
				self.match_classes[i].append(j)	
	
	
	del l11
	del l12
	del l13
	del l21
	del l22
	del l23
	for i in self.match_classes:
	    str1="%s: \n %s\n"%(i,self.match_classes[i])
	    file_d3.write(str1)
	self.method_ident={}
	self.ident_method_2nd=[]
	self.sim_method_2nd=[]
	for i in self.match_classes:
	    #file_d4.write("%s : %s\n"%(i,i.get_name()))
	    #file_d5.write("%s : %s\n"%(i,i.get_name()))
	    for j in i.cls_methd_ref:
		if j not in self.method_ident:
		    self.method_ident[j]=[]
		    #file_d4.write("\t%s : %s :%s\n"%(j,self.methd_hash_list[self.e1][j],self.method_ident[j]))	
		#if j not in self.method_simlr:
		    #self.method_simlr[j]=[]
		    #file_d5.write("\t%s : %s :%s\n"%(j,self.methd_hash_list[self.e1][j],self.method_simlr[j]))		
	  			  
	#file_d2.close()	    
	#file_d.close()
	#file_d1.close()
	#file_d3.close()
	#file_d4.close()
	#file_d5.close()
#-------------->>

#-------------->>
    def method_analysis(self,cls1,cls2,file_d=None): #Function to find the identical methods
	for i in cls1.cls_methd_ref:
	    for j in cls2.cls_methd_ref:
		if self.methd_hash_list[self.e1][i] == self.methd_hash_list[self.e2][j]:
		    self.method_ident[i].append(j)
		    #file_d.write("%s %s : %s : %s %s\n"%(i.get_class_name(),i.get_name(),self.methd_hash_list[self.e1][i],j.get_class_name(),j.get_name()))
		
#--------------!!

#-------------->>
    def find_sim_methds(self,mthd,methd_l,file_d=None): # Get similar method 
	methd_sim_val={}	
	for i in methd_l:
	    m1=self.e1.vmx.get_method_signature(mthd,predef_sign = DEFAULT_SIGNATURE).get_string()
	    m2=self.e2.vmx.get_method_signature(i,predef_sign = DEFAULT_SIGNATURE).get_string()
	    ncd,_=self.sim.ncd(m1,m2)
	    methd_sim_val[i]=ncd		
	    #file_d.write("%s %s %s:\n%s\n"%(mthd,mthd.get_class_name(),mthd.get_name(),m1))
	    #file_d.write("%s %s %s:\n%s\n%s\n\n"%(i,i.get_class_name(),i.get_name(),m2,ncd))
	m_sim_val=sorted(methd_sim_val.iteritems(),key=lambda (k,v):(v,k))
	#for i in range(0,len(m_sim_val)):
	    #file_d.write("%s : %s\n"%(i,m_sim_val[i][1]))	    		
	
	if m_sim_val[0][1]<0.4:	    	
	    return m_sim_val[0][0],m_sim_val[0][1]	    
	else: 
	    return None,None

#--------------!!

#-------------->>

    def get_diff_methd_apk2(self):
	n_diff_methd=0
	n_methd=0
	for i in self.methd_hash_list[self.e2]:
	    flag=0
	    n_methd+=1		
	    for j in self.method_ident:
		if i in self.method_ident[j]:
		    flag=1
		    break
	    if flag==0:
		n_diff_methd+=1
	return n_methd,n_diff_methd	 
#--------------!!

#-------------->>
    def sim_analysis(self):    # A function to find the identical and similar elements 
	#file_d=open('../Analysis_androgd/ident_method.txt','w') # Identical methods
	#file_d1=open('../Analysis_androgd/list_ident_method.txt','w') # List of identical methods
	#file_d2=open('../Analysis_androgd/Analysis_result.txt','w') # Contains final result 
	#file_d3=open('../Analysis_androgd/Not_Identical.txt','w') # Not identical in apk1 and apk2
	#file_d4=open('../Analysis_androgd/Not_Identical_list.txt','w') # Not identical
	#file_d5=open('../Analysis_androgd/sim_mthd_sig_nw.txt','w') # Conatins signature and ncd value ( for finding similar methods )
	self.sim_value_1apk=0.0
	self.sim_value_2apk=0.0
	self.sum_ncd_value=0.0
	self.methd_nt_ident={}
	val=0.0
	for i in self.match_classes:
	    for j in self.match_classes[i]:
#--------The original methd call is 2nd one
		self.method_analysis(i,j)
		#self.method_analysis(i,j,file_d)
	    mthd_diff=[]
	    	
	    val=0.0	
	    for k in i.cls_methd_ref:
		if len(self.method_ident[k])==0:
		    #file_d4.write("%s : %s %s \n"%(k,k.get_class_name(),k.get_name()))	
		    for j in self.match_classes[i]:
			for l in j.cls_methd_ref:
			    flag=0
			    for m in self.method_ident:
				if l in self.method_ident[m]:
				    flag=1
				    break
			    if flag==0:
				if l not in mthd_diff:
				    mthd_diff.append(l)
				    #file_d4.write("%s : %s %s\n"%(l,l.get_class_name(),l.get_name()))	
			#if len(mthd_diff)!=0:		
	    		    #file_d4.write("%s\n"%(mthd_diff))		    	    	
		    if i not in self.methd_nt_ident:	
		    	self.methd_nt_ident[i]={}
			#self.methd_nt_ident[i][k]={}
			if len(mthd_diff)!=0:
#--------The original methd call is 2nd one		
			    m_d,val=self.find_sim_methds(k,mthd_diff[:])	
			    #m_d,val=self.find_sim_methds(k,mthd_diff[:],file_d5)
			    self.methd_nt_ident[i][k]=m_d
			    if val == None:
				val=0.0	
			    if m_d not in self.sim_method_2nd and m_d is not None:
				self.sim_method_2nd.append(m_d)
		    else:
			#self.methd_nt_ident[i][k]={}
			if len(mthd_diff)!=0:
#--------The original methd call is 2nd one
			    m_d,val=self.find_sim_methds(k,mthd_diff[:])			
			    #m_d,val=self.find_sim_methds(k,mthd_diff[:],file_d5)
			    if val == None:
				val=0.0
			    self.methd_nt_ident[i][k]=m_d	
			    if m_d not in self.sim_method_2nd and m_d is not None:
				self.sim_method_2nd.append(m_d)
		    #file_d3.write("%s : %s\n%s\n"%(i.get_name(),k.get_name(),self.methd_nt_ident))		
		    #for j in self.match_classes[i]:
	            #for l in 
	    	self.sum_ncd_value+=float(val)
	    #if len(mthd_diff)!=0:		
	        #file_d4.write("%s\n"%(mthd_diff))
	avg_ncd_1apk=0.0
	avg_ncd_2apk=0.0
		
	#file_d.close()
	#file_d3.close()
	#file_d4.close()
	#file_d5.close()
	del mthd_diff
	
	for i in self.method_ident:
	    str1="%s %s :\n"%(i.get_class_name(),i.get_name())
	    #if len(self.method_ident[i]) == 0:
		#file_d1.write("Hii\n")
		#print ""
	    #else:
            if len(self.method_ident[i]) != 0:
	      	for j in self.method_ident[i]:
		    if j not in self.ident_method_2nd:
		    	self.ident_method_2nd.append(j)
		    #str1+="\t %s %s\n"%(j.get_class_name(),j.get_name())
	    #file_d1.write(str1)
	self.n_methd=0
	self.n_ident_methd=0
	n_nt_ident_methd=0
	for i in self.method_ident:
	    self.n_methd+=1
	    if self.method_ident[i]:
		self.n_ident_methd+=1
	    else:
		n_nt_ident_methd+=1	
	self.n_sim_methd=0
	if n_nt_ident_methd:
	    for i in self.methd_nt_ident:
		for j in self.methd_nt_ident[i]:
		    if self.methd_nt_ident[i][j]:
			self.n_sim_methd+=1
	self.n_diff_methd=n_nt_ident_methd-self.n_sim_methd
	self.n_2nd_methd = len(self.methd_hash_list[self.e2])
        #self.n_2nd_methd,diff_2nd_methd=self.get_diff_methd_apk2()
	#self.n_2nd_diff_methd=diff_2nd_methd-self.n_sim_methd  	
	#file_d2.write("No: identical method: %d\nNo: of similar method: %d\nNo: of different method: %d\nNo: of diff method in apk2: %d\nTotal no: of method %d\nTotal no: of method in apk2: %d\n"%(self.n_ident_methd,self.n_sim_methd,self.n_diff_methd,self.n_2nd_diff_methd,self.n_methd,self.n_2_methd))	
	#file_d2.write("No: identical method: %d\nNo: of similar method: %d\nNo: of different method: %d\nTotal no: of method %d\n"%(self.n_ident_methd,self.n_sim_methd,self.n_diff_methd,self.n_methd))	
	#file_d2.close()	
	#file_d1.close()
	if self.sum_ncd_value:	
	    avg_ncd_1apk=float(self.sum_ncd_value)/float(self.n_sim_methd)
	    avg_ncd_2apk=float(self.sum_ncd_value)/float(len(self.sim_method_2nd))
	self.sim_value_1apk=(float(self.n_ident_methd+self.n_sim_methd*(1-avg_ncd_1apk))/float(self.n_methd))*100
	self.sim_value_2apk=(float(len(self.ident_method_2nd)+len(self.sim_method_2nd)*(1-avg_ncd_1apk))/float(self.n_2nd_methd))*100	
			
#--------------!!

#-------------->>
    def print_final_rslt(self,file1_name,file2_name,apk1_v=None,apk2_v=None):
	file_d=open("../Analysis_androgd/exodus/Analysis_result_%s_%s.txt"%(file1_name,file2_name),'w')
	file_d.write("No: identical method in apk1: %d\nNo: identical method in apk2: %d\nNo: of similar method in apk1: %d\nNo: of similar method in apk2: %d\nNo: of different method in apk1: %d\nNo: of different method in apk2: %d\nTotal no: of method in apk1:  %d\nTotal no: of method in apk1:  %d\nSimilarity Value based on apk1 %f %% \nSimilarity Value based on apk2 %f %% \nAPK1_version: %s\nAPK2_version: %s\n"%(self.n_ident_methd,len(self.ident_method_2nd),self.n_sim_methd,len(self.sim_method_2nd), self.n_diff_methd,(self.n_2nd_methd-(len(self.ident_method_2nd)+len(self.sim_method_2nd))), self.n_methd, self.n_2nd_methd, self.sim_value_1apk,self.sim_value_2apk, apk1_v, apk2_v))
	file_d.close()
#--------------!!

    def _init_similarity(self) :
        intersection_elements = self.set_els[ self.e2 ].intersection( self.set_els[ self.e1 ] ) 
        difference_elements = self.set_els[ self.e2 ].difference( intersection_elements )
#--------	
	#print intersection_elements
	#print difference_elements
	#print self.ref_set_els[self.e2]
        self.filters[IDENTICAL_ELEMENTS].update([ self.ref_set_els[ self.e1 ][ i ] for i in intersection_elements ])
        available_e2_elements = [ self.ref_set_els[ self.e2 ][ i ] for i in difference_elements ]
#--------
	#print self.ref_set_els[self.e2]
	#print [self.ref_set_els[self.e2][i] for i in difference_elements ]	
	print available_e2_elements
        # Check if some elements in the first file has been modified
        for j in self.filters[ELEMENTS][self.e1] :
            self.filters[ SIMILARITY_ELEMENTS ][ j ] = {}

            #debug("SIM FOR %s" % (j.get_info()))
            if j.getsha256() not in self.filters[HASHSUM][self.e2] :
                
                #eln = ElsimNeighbors( j, available_e2_elements )
                #for k in eln.cmp_elements() :
                for k in available_e2_elements :
                    #debug("%s" % k.get_info()) 
                    self.filters[SIMILARITY_ELEMENTS][ j ][ k ] = self.filters[BASE][FILTER_SIM_METH]( self.sim, j, k )
		    #print "%s:%s:%s"%(j,k,self.filters[SIMILARITY_ELEMENTS][j][k])
                    if j.getsha256() not in self.filters[HASHSUM_SIMILAR_ELEMENTS] :
                        self.filters[SIMILAR_ELEMENTS].append(j)
                        self.filters[HASHSUM_SIMILAR_ELEMENTS].append( j.getsha256() )
#------
	#print self.filters[SIMILARITY_ELEMENTS]
	#print self.filters[SIMILAR_ELEMENTS]
			

    def _init_sort_elements(self) :
        deleted_elements = []
#--------
	#print "soooooo"	
        for j in self.filters[SIMILAR_ELEMENTS] :
            #debug("SORT FOR %s" % (j.get_info()))
            
            sort_h = self.filters[BASE][FILTER_SORT_METH]( j, self.filters[SIMILARITY_ELEMENTS][ j ], self.filters[BASE][FILTER_SORT_VALUE] )
            self.filters[SIMILARITY_SORT_ELEMENTS][ j ] = set( i[0] for i in sort_h )
#----------
	    #print sort_h	
            ret = True
            if sort_h == [] :
                ret = False

            if ret == False :
                deleted_elements.append( j )

        for j in deleted_elements :
            self.filters[ DELETED_ELEMENTS ].append( j )
            self.filters[ SIMILAR_ELEMENTS ].remove( j )
        
    def __checksort(self, x, y) :
        return y in self.filters[SIMILARITY_SORT_ELEMENTS][ x ]

    def _init_new_elements(self) :
        # Check if some elements in the second file are totally new !
        for j in self.filters[ELEMENTS][self.e2] :

            # new elements can't be in similar elements
            if j not in self.filters[SIMILAR_ELEMENTS] :
                # new elements hashes can't be in first file
                if j.getsha256() not in self.filters[HASHSUM][self.e1] :
                    ok = True
                    # new elements can't be compared to another one
                    for diff_element in self.filters[SIMILAR_ELEMENTS] :
                        if self.__checksort( diff_element, j ) :
                            ok = False
                            break

                    if ok :
                        if j.getsha256() not in self.filters[HASHSUM_NEW_ELEMENTS] :
                            self.filters[NEW_ELEMENTS].add( j )
                            self.filters[HASHSUM_NEW_ELEMENTS].append( j.getsha256() )

    def get_similar_elements(self) :
        """ Return the similar elements
            @rtype : a list of elements
        """
        return self.get_elem( SIMILAR_ELEMENTS )

    def get_new_elements(self) :
        """ Return the new elements
            @rtype : a list of elements
        """
        return self.get_elem( NEW_ELEMENTS )
    
    def get_deleted_elements(self) :
        """ Return the deleted elements
            @rtype : a list of elements
        """
        return self.get_elem( DELETED_ELEMENTS )
    
    def get_internal_identical_elements(self, ce) :
        """ Return the internal identical elements 
            @rtype : a list of elements
        """
        return self.get_elem( INTERNAL_IDENTICAL_ELEMENTS )

    def get_identical_elements(self) :
        """ Return the identical elements 
            @rtype : a list of elements
        """
        return self.get_elem( IDENTICAL_ELEMENTS )
    
    def get_skipped_elements(self) :
        return self.get_elem( SKIPPED_ELEMENTS )

    def get_elem(self, attr) :
        return [ x for x in self.filters[attr] ]

    def show_element(self, i, details=True) :
        print "\t", i.get_info()

        if details :
            if i.getsha256() == None :
                pass
            elif i.getsha256() in self.ref_set_els[self.e2]:
                if len(self.ref_set_ident[self.e2][i.getsha256()]) > 1:
                    for ident in self.ref_set_ident[self.e2][i.getsha256()]:
                        print "\t\t-->", ident.get_info()
                else:
                    print "\t\t-->", self.ref_set_els[self.e2][ i.getsha256() ].get_info()
            else :
                for j in self.filters[ SIMILARITY_SORT_ELEMENTS ][ i ] :
                    print "\t\t-->", j.get_info(), self.filters[ SIMILARITY_ELEMENTS ][ i ][ j ]
    
    def get_element_info(self, i) :
        
        l = []

        if i.getsha256() == None :
            pass
        elif i.getsha256() in self.ref_set_els[self.e2] :
            l.append( [ i, self.ref_set_els[self.e2][ i.getsha256() ] ] )
        else :
            for j in self.filters[ SIMILARITY_SORT_ELEMENTS ][ i ] :
                l.append( [i, j, self.filters[ SIMILARITY_ELEMENTS ][ i ][ j ] ] )
        return l

    def get_associated_element(self, i) :
        return list(self.filters[ SIMILARITY_SORT_ELEMENTS ][ i ])[0]

    def get_similarity_value(self, new=True) :
        values = []

        self.sim.set_compress_type( BZ2_COMPRESS )
#-------
	#print "hiiiiiiii"
	#print self.filters[SIMILAR_ELEMENTS]
        for j in self.filters[SIMILAR_ELEMENTS] :

            k = self.get_associated_element( j )
	
            value = self.filters[BASE][FILTER_SIM_METH]( self.sim, j, k )
            # filter value
            value = self.filters[BASE][FILTER_SIM_VALUE_METH]( value )

            values.append( value )

        values.extend( [ self.filters[BASE][FILTER_SIM_VALUE_METH]( 0.0 ) for i in self.filters[IDENTICAL_ELEMENTS] ] )
        if new == True :
            values.extend( [ self.filters[BASE][FILTER_SIM_VALUE_METH]( 1.0 ) for i in self.filters[NEW_ELEMENTS] ] )
        else :
            values.extend( [ self.filters[BASE][FILTER_SIM_VALUE_METH]( 1.0 ) for i in self.filters[DELETED_ELEMENTS] ] )

        self.sim.set_compress_type( self.compressor )
#-------
	#print values
        similarity_value = 0.0
        for i in values :
            similarity_value += (1.0 - i)

        if len(values) == 0 :
            return 0.0

        return (similarity_value/len(values)) * 100

    def show(self): 
        print "Elements:"
        print "\t IDENTICAL:\t", len(self.get_identical_elements())
        print "\t SIMILAR: \t", len(self.get_similar_elements())
        print "\t NEW:\t\t", len(self.get_new_elements())
        print "\t DELETED:\t", len(self.get_deleted_elements())
        print "\t SKIPPED:\t", len(self.get_skipped_elements())

        #self.sim.show()

ADDED_ELEMENTS = "added elements"
DELETED_ELEMENTS = "deleted elements"
LINK_ELEMENTS = "link elements"
DIFF = "diff"
class Eldiff :
    def __init__(self, elsim, F) :
        self.elsim = elsim
        self.F = F
       
        self._init_filters()
        self._init_diff()

    def _init_filters(self) :
        self.filters = {}

        self.filters[ BASE ]                = {}
        self.filters[ BASE ].update( self.F )
        self.filters[ ELEMENTS ]            = {}
        self.filters[ ADDED_ELEMENTS ] = {} 
        self.filters[ DELETED_ELEMENTS ] = {}
        self.filters[ LINK_ELEMENTS ] = {}

    def _init_diff(self) :
        for i, j in self.elsim.get_elements() :
            self.filters[ ADDED_ELEMENTS ][ j ] = []
            self.filters[ DELETED_ELEMENTS ][ i ] = []

            x = self.filters[ BASE ][ DIFF ]( i, j )

            self.filters[ ADDED_ELEMENTS ][ j ].extend( x.get_added_elements() )
            self.filters[ DELETED_ELEMENTS ][ i ].extend( x.get_deleted_elements() )

            self.filters[ LINK_ELEMENTS ][ j ] = i
            #self.filters[ LINK_ELEMENTS ][ i ] = j

    def show(self) :
        for bb in self.filters[ LINK_ELEMENTS ] : #print "la"
            print bb.get_info(), self.filters[ LINK_ELEMENTS ][ bb ].get_info()
            
            print "Added Elements(%d)" % (len(self.filters[ ADDED_ELEMENTS ][ bb ]))
            for i in self.filters[ ADDED_ELEMENTS ][ bb ] :
                print "\t",
                i.show()

            print "Deleted Elements(%d)" % (len(self.filters[ DELETED_ELEMENTS ][ self.filters[ LINK_ELEMENTS ][ bb ] ]))
            for i in self.filters[ DELETED_ELEMENTS ][ self.filters[ LINK_ELEMENTS ][ bb ] ] :
                print "\t",
                i.show()
            print

    def get_added_elements(self) :
        return self.filters[ ADDED_ELEMENTS ]

    def get_deleted_elements(self) :
        return self.filters[ DELETED_ELEMENTS ]
