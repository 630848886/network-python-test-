import sys, os, glob

print 'Called filter() function in filter_packets.py'

def filter( filename, L):
    f = open(filename, 'r')
    line = f.readline()

    while line:
       line = f.readline()
       if "ICMP" in line and "Echo" in line:
          line = line.strip()
          L.append(line)
          line = f.readline()
    f.close()
  
    i = 1
    while os.path.exists("Node%s_filtered.txt" % i ):
        i += 1

    with open("Node%s_filtered.txt" % i, "w") as f:
	i += 1
        for item in L:
            f.write("%s\n" % item)
    f.close()

#main
#Remove any previously existing filtered files
for filename in glob.glob('*filtered.txt*') :
    os.remove( filename )

A = []
B = []
C = []
D = []
E = []

#Original Files
file1 = 'Node1.txt'
file2 = 'Node2.txt'
file3 = 'Node3.txt'
file4 = 'Node5.txt'
file5 = 'Node5.txt'

#Read in a filter ICMP data into lists
filter(file1, A)
filter(file2, B)
filter(file3, C)
filter(file4, D)
filter(file5, E)
