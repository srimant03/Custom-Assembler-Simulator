import sys
Inst = {"add":"10000", "sub":"10001", "mov":"", "movi":"10010", "movr":"10011", "ld":"10100", "st":"10101", "mul":"10110", "div":"10111",
    "rs":"11000", "ls":"11001", "xor":"11010", "or":"11011", "and":"11100", "not":"11101", "cmp":"11110", 
    "jmp":"11111", "jlt":"01100", "jgt":"01101", "je":"01111", "hlt":"01010","addf":"00000","subf":"00001","movf":"00010"}
    
Reg ={"R0":"000", "R1":"001", "R2":"010", "R3":"011", "R4":"100", "R5":"101", "R6":"110", "FLAGS":"111"}

A=["add", "sub", "mul", "xor", "or", "and","addf","subf"] #2 unused bits
B=["mov", "ls", "rs","movf"]
C=["cmp", "mov", "not", "div"] #5 unused bits
D=["ld", "st"]
E=["jlt", "jmp", "jgt", "je"] #3 unused bits
F=["hlt"] #11 unused bits

def float_converter(n):
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
    return y

def isfloat(str):
    check=1
    for i in str:
        if(i!="." and (i<"0" or i>"9")):
            check=0
            break
    return check


def float_ieee(f):
    pos=f.index(".")
    f=f[1:6]
    exp=bin(pos-1)
    exp=exp[2:]
    diff=3-len(exp)
    exp="0"*diff + exp

    res=exp + f[0:pos] + f[pos+1:]
    return res

def decimal_binary(n):
    res=0
    pow=0
    while(n>0):
        res=res+ (n%2)*(10**pow)
        pow+=1
        n=n//2
    num=str(res)
    diff=8-len(num)
    num="0"*diff + num
    return num

Var=[]
Label={}
Output=[]

S=sys.stdin.readlines()

counter=0
error=0
lines=0

for i in range(0,len(S)):
    p=[i for i in S[i].strip().split()]
    if len(p)==0:
        continue 
    elif p[0]=="var":
        continue
    else:
        lines+=1
lines=lines-1
countf=-1
for i in range(0,len(S)):
    p=[i for i in S[i].strip().split()]
    if len(p)==0:
        continue
    elif p[0]=="var":
        continue
    elif (p[0][len(p[0])-1]==":"):
        countf+=1
        z=p[0][:-1]
        Label[z]=decimal_binary(countf)
    else:
        countf+=1

var_flag=0
hlt_flag=0
for i in range(0, len(S)):
    L=[i for i in S[i].strip().split()]
    counter+=1
    if len(L)==0:
        continue
    else:
        if(L[0][len(L[0])-1]==":"):
            L.pop(0)
        op=L[0]   
        res=""
        error=0
        if op=="var":
            if len(L)!=2:
                error=1
                break
            if var_flag==0:
                if ((L[1]) in Reg) or (L[1] in Inst):
                    error=10
                    break
                if not L[1].isdigit():
                    Var.append(L[1])
                    continue
                else:
                    error=10
                    break
            else:
                error=7
                break
        elif op not in Inst:      
            error=1
            break  
        else:
            var_flag=1
            if op!="mov":
                res+=Inst[op]
            else:
                if L[2][0]=="$":
                    res+=Inst["movi"]
                else:
                    res+=Inst["movr"]
            if op in A:
                if(len(L)!=4):
                    error=1
                    break
                elif(L[1] not in Reg or L[2] not in Reg or L[3] not in Reg):
                    error=1
                    break
                res+="0"*2
            elif op=="mov":
                if L[2]=="FLAGS":
                    error=4
                    break
                if L[1]=="FLAGS":
                    res+="0"*5
                    res+="1"*3
                elif L[2][0]!="$":
                    res+="0"*5
                elif(L[2][0]=="$"):
                    if (float(L[2][1::])-int(float(L[2][1::]))!=0):
                        error=5
                        break
                    elif (int(L[2][1::])>255 or int(L[2][1::])<0):
                        error=5
                        break
            elif op in B or op in C:
                if(len(L)!=3):
                    error=1
                    break
                elif(L[1] not in Reg):
                    error=1
                    break
                elif(L[2] not in Reg):
                    if(L[2][0]=="$" and L[0]=="movf"):
                        if(isfloat(L[2][1::])==0):
                            error=1
                            break
                        elif (float(L[2][1::])>252 or float(L[2][1::])<0):
                            error=5
                            break
                    elif(L[2][0]=="$" and L[0]!="movf"):                            
                        if(not L[2][1::].isdigit()):
                            error=1
                            break
                        elif (int(L[2][1::])>255 or int(L[2][1::])<0):
                            error=5
                            break
                    else:
                        error=1
                        break
                else:
                    res+="0"*5            
            elif op in D:
                if(len(L)!=3):
                    error=1
                    break
                elif(L[1] not in Reg):
                    error=1 
                    break
                elif(L[2] not in Var):
                    if(L[2] in Label):
                        error=6
                        break
                    else:
                        error=2
                        break

            elif op in E:
                if(len(L)!=2):
                    error=1
                    break
                if (L[1] not in Label):
                    if(L[1] in Var):
                        error=6
                        break
                    else:
                        error=3
                        break 
                else:
                    res+="0"*3
                    res+=str(Label[L[1]])
            elif op in F:
                res+="0"*11
                hlt_flag=i+1
                if(hlt_flag<(len(S))):
                    error=9
                    break
            for j in L:
                if j!=op:
                    if j[0]=="$" and L[0]=="movf":
                        res+=float_ieee(float_converter(float(j[1::])))
                    elif j[0]=="$" and L[0]!="movf":
                        res+=decimal_binary(int(j[1::]))
                    elif j in Var:
                        y=lines+(Var.index(j)+1)
                        res+=decimal_binary(y)
                    else:
                        if j=="FLAGS":
                            if L[0]!="mov":
                                error=4
                                break
                        elif j in Reg:
                            res+=Reg[j]
            if error==4:
                break
            Output.append(res)
if hlt_flag==0 and error==0:
    error=8


if(error==0):
    for i in range(0, len(Output)):
        if(i<len(Output)-1):
            sys.stdout.write(Output[i]+"\n")
        else:
            sys.stdout.write(Output[i])
elif (error==1):
    print("Syntax error in line",i+1) 
elif (error==2):
    print("Variable not declared in line",i+1) 
elif (error==3):
    print("Label not declared in line",i+1) 
elif (error==4):
    print("Illegal use of flags in line", i+1) 
elif (error==5):
    print("Illegal immediate values in line",i+1) 
elif (error==6):
    print("Misuse of lables in line",i+1) 
elif (error==7):
    print("Variables not declared in the beginning") 
elif (error==8):
    print("missing halt instructions") 
elif (error==9):
    print("Halt instruction not being used in the last") 
elif (error==10):
    print("Invalid variable name")