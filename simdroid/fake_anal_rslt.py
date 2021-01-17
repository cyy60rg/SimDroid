#!/usr/bin/python

import os
file_d=open("../Analysis_androgd/Final_analysis_rslt.txt",'w')
file_d.write("{0:25} {1:25} {2:25} {3:30}     {4:15} {5:10} {6:10} {7:10}\n\n".format("Apk1_src","Apk1","Ap2_src","Apk2","No_Ident","No_Sim","No_Diff","Tot_No_Mthd"))
targ_dir="../Analysis_androgd/Result"
i=0
for file in os.listdir(targ_dir):
    i=0
    if file.endswith(".txt"):
        print file
        file_nm=os.path.splitext(file)[0]
        l=file_nm.split('_')
	print l
        apk1=""
	apk2_src="" 
        #print l[2]
        apk1_src=l[2]
	if "aosb" in l:
	    n=l.index("aosb")
	    print n
	    if n == 2:
	    	apk2_src=l[6]
	    	apk1=l[5]
	    elif n==4:
	    	apk2_src=l[4]
		apk1=l[3]
	else:
	    apk2_src=l[4]
	    apk1=l[3]		 
	apk2=l[-1]
	

        file_d1=open("%s/%s"%(targ_dir,file),'r')
        l=[]
        for line in file_d1:
            for s in line.split():
                if s.isdigit():
                    l.append(int(s))
        file_d1.close()            
        file_d.write("{0:25} {1:25} {2:25} {3:25}     {4:12} {5:12} {6:12} {7:12}\n".format(apk1_src,apk1,apk2_src,apk2,l[0],l[1],l[2],l[3]))
file_d.close()        
