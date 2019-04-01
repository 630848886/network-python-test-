import re

print 'Called parse() function in packet_parser.py'

def parse(filename, L):
    f = open(filename, 'r')
    line = f.readline()

    while line:
        line = line.replace(',', '')
        line = line.strip().split()

        time = float(line[1])
        src = str(line[2])
        dst = str(line[3])
        len = int(line[5])
        seq = str(line[10])
        seq = int(seq[4:6])
        ttl = str(line[11])
        ttl = int(ttl[4:8])
        type = str(line[8])

        M =[]

        M.append(time)
        M.append(src)
        M.append(dst)
        M.append(len)
        M.append(seq)
        M.append(ttl)
        M.append(type)

        M = [time, src, dst, len, seq, ttl, type]

        L.append(M)

        line = f.readline()

#main
A = []
B = []
C = []
D = []
E = []

#Take in filtered files
file1 = 'Node1_filtered.txt'
file2 = 'Node2_filtered.txt'
file3 = 'Node3_filtered.txt'
file4 = 'Node4_filtered.txt'
file5 = 'Node5_filtered.txt'
#Parse the filted files into lists for computation
parse(file1, A)
parse(file2, B)
parse(file3, C)
parse(file4, D)
parse(file5, E)


	
