import sys
#import matplotlib.pyplot as plt

def bit_extender(s, size):
    diff=size-len(s)
    s=("0"*diff)+s
    return s

def binary_decimal(n): 
    n=str(n)
    pow=len(n)-1
    res=0
    for i in n:
        res+=(2**pow)*int(i)
        pow-=1
    return res
        
def decimal_binary(n):
    n=int(n)
    res=0
    pow=0
    while(n>0):
        res=res+ (n%2)*(10**pow)
        pow+=1
        n=n//2    
    res=str(res)
    result=bit_extender(res, 8)
    return result

def ieee_decimal(n):
    exp=binary_decimal(n[0:3])
    num=binary_decimal("1"+n[3:8])
    shift=exp-5
    res=num*pow(2, shift)
    return res    

def decimal_ieee(n): #Bit extender
    float(n)
    f=n%1
    w=n//1
    w=bin(int(w))
    w=w[2:]
    x=""
    for i in range(0,4):
        f*=2
        if f>=1:
            f=f%1
            x+="1"
        else:
            f*=2
            x+="0"
    y=""
    y+=str(w)+"."+x
    pos=y.index(".")
    exp=bin(pos-1)
    exp=exp[2:]
    exp=str(exp)
    diff=3-len(exp)
    exp="0"*diff + exp
    res=""
    y=y.replace(".","")
    z=""
    if len(y[1:6])<5:
        z+=y[1:6]+str(0*(5-len(y[1:6])))
    res=res+exp+z
    return res    
    
A ={"10000":"add", "10001":"sub", "10110":"mul", "11010":"xor", "11011":"or", "11100":"and","00000":"addf","00001":"subf"}
B={"10010":"movi", "11000":"rs", "11001":"ls","00010":"movf"}
C={"11110":"cmp", "10011":"movr", "10111":"div", "11101":"not"}
D={"10100":"ld", "10101":"st"}
E={"11111":"jmp", "01100":"jlt", "01101":"jgt", "01111":"je"}
F={"01010":"hlt"}

Registers ={"000":0, "001":1, "010":2, "011":3, "100":4, "101":5, "110":6,"111":"flags"}
Variables = {}

RF=["00000000", "00000000", "00000000", "00000000", "00000000", "00000000", "00000000"] # R0-R6 registers
FLAGS=[0, 0, 0, 0]
PC, Cycle, halted, flag_flip=0, 0, 0, 0

def load_memory(Mem, Inp, n):
    for i in range(0, n):
        Mem[i]=Inp[i].strip()
    return

def bit_extender(s, size):
    diff=size-len(s)
    s=("0"*diff)+s
    return s

def Update_PC (new_PC):
    global PC
    PC=new_PC
    return

def display_state():
    global PC
    print(bit_extender( str(decimal_binary(PC)), 8), end=" ")   
    for i in RF:
        print(bit_extender(i, 16), end=" ")
    flg="".join(str(i) for i in FLAGS)
    for i in FLAGS:
        flg+=str(i)    
    print(bit_extender(flg, 16))
    return

def display_Memory():
    for i in Mem:
        print(i)

def A_execute(operator, r1, r2, r3, PC, flag_flip):
    res=0
    n2=binary_decimal(RF[r2])
    n3=binary_decimal(RF[r3])
    ne2=ieee_decimal(RF[r2])
    ne3=ieee_decimal(RF[r3])
    if operator=="add":
        res= n2 + n3
    elif operator=="sub":
        res= n2 - n3
    elif operator=="mul":
        res= n2 * n3
    elif operator=="xor":
        res= n2 ^ n3
    elif operator=="or":
        res= n2 | n3
    elif operator=="and":
        res= n2 & n3
    elif operator=="addf":
        res= ne2 + ne3
    elif operator=="subf":
        res= ne2 - ne3
    
    if operator=="addf" or operator=="subf":
        if res>252:
            flag_flip=1
            res=252
            FLAGS[0]=1
            
        elif res<0:
            flag_flip=1
            res=0
            FLAGS[0]=1
            
        RF[r1]=decimal_binary(res)
    else:
        if res>255:
            flag_flip=1
            res=252
            FLAGS[0]=1
            
        elif res<0:
            flag_flip=1
            res=0
            FLAGS[0]=1
            
        RF[r1]=decimal_ieee(res)
    PC+=1
    return PC, flag_flip

def B_execute(operator, r1, val, PC):
    n1=binary_decimal(RF[r1])
    if operator=="ls":
        res=n1<<val
    elif operator=="rs":
        res=n1>>val
    elif operator=="movi":
        res=val    
    RF[r1]=decimal_binary(res)
    PC+=1
    return PC
    
def C_execute(operator, r1, r2, PC, flag_flip):
    n1=binary_decimal(RF[r1])
    n2=binary_decimal(RF[r2])
    if operator=="movr":
        if r1!="flags":
            RF[r1]=RF[r2]
        elif r1=="flags":
            f="".join(str(i) for i in FLAGS)
            RF[r2]=bit_extender(f, 8)
    elif operator=="not":
        RF[r1]= decimal_binary(255 - n2)
    elif operator=="div":
        RF[0]=decimal_binary(n1 // n2)
        RF[1]=decimal_binary(n1 % n2)
    elif operator=="cmp":
        if n1==n2:
            flag_flip=1
            FLAGS[3]=1
        elif n1>n2:
            flag_flip=1
            FLAGS[2]=1
        elif n1<n2:
            if FLAGS[1]==1:
                flag_flip=0
            else:
                flag_flip=1
            FLAGS[2]=1    
    PC+=1
    return PC, flag_flip

def D_execute(operator, r1, address, PC): 
    if operator=="st":
        Variables[address]=RF[r1]
    elif operator=="ld":
        if address not in Variables:  
            Variables[address]=decimal_binary(0)   
        RF[r1]=Variables[address]        
    PC+=1
    return PC

def E_Execute(operator, jmp_address, PC):
    if operator=="jmp":
        PC=jmp_address
    elif operator=="jlt":
        if FLAGS[1]==1:
            PC=jmp_address
        else:
            PC+=1
    elif operator=="jgt":
        if FLAGS[2]==1:
            PC=jmp_address
        else:
            PC+=1
    elif operator=="je":
        if FLAGS[3]==1:
            PC=jmp_address
        else:
            PC+=1
    return PC
        
def Execute(Inst, flag_flip, PC):
    hlt=0
    op=Inst[0:5]    
    if op in A:
        PC, flag_flip=A_execute(A[op], Registers[Inst[7:10]], Registers[Inst[10:13]], Registers[Inst[13:16]], PC, flag_flip)
        
    elif op in B:
        PC=B_execute(B[op], Registers[Inst[5:8]] , binary_decimal(Inst[8:16]), PC)  

    elif op in C:
        PC, flag_flip=C_execute(C[op], Registers[Inst[10:13]], Registers[Inst[13:16]], PC, flag_flip)

    elif op in D:
        PC=D_execute(D[op], Registers[Inst[5:8]], Inst[8:16], PC)

    elif op in E:
        PC=E_Execute(E[op], binary_decimal(Inst[8:16]), PC)
    elif op in F:
        hlt=1
    return hlt, flag_flip, PC

L_Cycle=[]
L_PC=[]

Mem=["0"*16]*256
Inp=sys.stdin.readlines()
lines=[]
for i in Inp:
    i=i.strip()
    if i:
        lines.append(i)
n=len(lines)
# print(n)
load_memory(Mem, lines, n)
while halted==0:
    Cycle+=1
    flag_flip=0
    Inst=Mem[PC]
    halted, flag_flip, new_PC = Execute(Inst, flag_flip, PC)
    if(flag_flip==0):
        FLAGS=[0, 0, 0, 0]
    display_state()
    L_Cycle.append(Cycle)
    L_PC.append(PC)
    Update_PC(new_PC)

Sorted_Variables=sorted(Variables)
for i in Sorted_Variables:
    x=str(decimal_binary(Variables[i]))
    x=bit_extender(x, 16)
    lines.append(x)
n=len(lines)
load_memory(Mem, lines, n)
display_Memory()

#Graph
#plt.scatter(L_Cycle,L_PC,c="pink",edgecolors="face")
#plt.title("Cycle vs Memory Address")
#plt.xlabel("Cycles")
#plt.ylabel("Memory Address")
#plt.show()
