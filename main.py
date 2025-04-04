import re

def to_number(s):
    if s in ["-", ".", "-."]:
        return float(0)
    else:
        return float(s) 

def is_number(s):
    if not s:
        return False
    num_re = r"-?\d*\.?\d*"
    match = re.match(num_re, s)
    return s == match.group()

def handle(bytecodes, i = 0):
    command_re = r"\s*(?P<opcode>[A-Z]+)\s?(?P<arg1>[a-zA-z0-9_\-.]+)?,?\s?(?P<arg2>[a-zA-z0-9_\-.]+)?$"

    regs = {
        "AX" : 0,
        "BX" : 0,
        "CX" : 0,
        "DX" : 0,
        "SP" : -1,
        "BP" : 0,
    }
    
    FLAGS = 0 #E NE G L
    E = 1
    NE = 2
    G = 4
    L = 8

    STACK = []
    
    VARS = []

    max_i = 0
    for key in bytecodes.keys():
        if isinstance(key, int):
            max_i += 1

    while i < max_i:
        if i not in bytecodes:
            print(f"{i}: Unknown line")
            return

        if bytecodes[i] == "":
            i += 1
            continue

        match = re.search(command_re, bytecodes[i])
        
        if match is None:
            print(f"{i}: Unknown command")
            return

        opcode = match.group('opcode')
        arg1 = match.group('arg1')
        arg2 = match.group('arg2')

        match opcode:
            case "MOV":
                if arg1 in regs:
                    if arg2 in regs:
                        regs[arg1] = regs[arg2]
                    elif is_number(arg2):
                        regs[arg1] = to_number(arg2)
                    else:
                        print(f"{i}: Invalid second argument")
                        return
                else:
                    print(f"{i}: Invalid first argument")
                    return
            
            #arithmetic operations
            case "ADD": 
                if arg1 in regs:
                    if arg2 in regs:
                        regs[arg1] = regs[arg1] + regs[arg2]
                    elif is_number(arg2):
                        regs[arg1] = regs[arg1] + to_number(arg2)
                    else:
                        print(f"{i}: Invalid second argument")
                        return
                else:
                    print(f"{i}: Invalid first argument")
                    return

            case "SUB": 
                if arg1 in regs:
                    if arg2 in regs:
                        regs[arg1] = regs[arg1] - regs[arg2]
                    elif is_number(arg2):
                        regs[arg1] = regs[arg1] - to_number(arg2)
                    else:
                        print(f"{i}: Invalid second argument")
                        return
                else:
                    print(f"{i}: Invalid first argument")
                    return
            
            case "MULT": 
                if arg1 in regs:
                    if arg2 in regs:
                        regs["DX"] = regs[arg1] * regs[arg2]
                    elif is_number(arg2):
                        regs["DX"] = regs[arg1] * to_number(arg2)
                    else:
                        print(f"{i}: Invalid second argument")
                        return
                else:
                    print(f"{i}: Invalid first argument")
                    return
            
            case "DIV": 
                if arg1 in regs:
                    if arg2 in regs:
                        regs["DX"] = regs[arg1] / regs[arg2]
                    elif is_number(arg2):
                        regs["DX"] = regs[arg1] / to_number(arg2)
                    else:
                        print(f"{i}: Invalid second argument")
                        return
                else:
                    print(f"{i}: Invalid first argument")
                    return
            
            #stack operations
            case "PUSH":
                if arg1 in regs:
                    regs["SP"] += 1
                    STACK.append( regs[arg1] )
                elif is_number(arg1):
                    regs["SP"] += 1
                    STACK.append( to_number(arg1) )
                else:
                    print(f"{i}: Invalid argument")
                    return

            case "POP":
                if arg1 in regs:
                    if regs["SP"] < 0:
                        print(f"{i}: Stack is empty")
                        return
                        
                    elif regs["SP"] < regs["BP"]:
                        print(f"{i}: You went out of your stack frame")
                        return
                        
                    regs["SP"] -= 1
                    regs[arg1] = STACK.pop()
                else:
                    print(f"{i}: Invalid argument")
                    return
          
            #call operations 
            case "CALL":
                if arg1 in regs:
                    if isinstance(regs[arg1], int):
                        regs["SP"] += 1
                        STACK.append(i + 1)
                        i = regs[arg1]
                        continue
                    else:
                        print(f"{i}: Line number must be integer")
                        return
                elif arg1.isdigit():
                    regs["SP"] += 1
                    STACK.append(i + 1)
                    i = int(arg1)
                    continue
                elif arg1 in bytecodes:
                    regs["SP"] += 1
                    STACK.append(i + 1)
                    i = bytecodes[arg1]
                    continue
                else:
                    print(f"{i}: Invalid argument or label")
                    return

            case "CLEARF":
                diff = regs["SP"] - regs["BP"]
                if diff < 0:
                    print(f"{i}: SP is lower than BP")
                    return
                elif diff > 0:
                    regs["SP"] = regs["BP"]
                    try:
                        del STACK[regs["BP"] + 1:]
                    except Exception as e:
                        print(f"{i}: Can not clear stack frame because {e}")

            case "RET":
                if regs["SP"] < 0:
                    print(f"{i}: Stack is empty")
                    return
                        
                elif regs["SP"] < regs["BP"]:
                    print(f"{i}: You did not restore BP")
                    return
                        
                regs["SP"] -= 1
                i = STACK.pop()
                continue

            case "PRINTSTACK":
                print(STACK)

            #compare
            case "CMP":
                left = None
                right = None
                if arg1 in regs and arg2 in regs:
                    left = regs[arg1]
                    right = regs[arg2]
                elif arg1 in regs and is_number(arg2):
                    left = regs[arg1]
                    right = to_number(arg2)
                elif is_number(arg1) and arg2 in regs:
                    left = to_number(arg1)
                    right = regs[arg2]
                elif is_number(arg1) and is_number(arg2):
                    left = to_number(arg1)
                    right = to_number(arg2)
                else:
                    print(f"{i}: Ivalid first/second/both argument(s)")
                    return

                FLAGS = 0
                if left == right:
                    FLAGS |= 1
                elif left < right:
                    FLAGS |= 8
                    FLAGS |= 2
                elif left > right:
                    FLAGS |= 4
                    FLAGS |= 2    

            #jumps
            case "JMP":
                if arg1 in regs:
                    if isinstance(regs[arg1], int):
                        i = regs[arg1]
                        continue
                    else:
                        print(f"{i}: Line number must be integer")
                        return
                elif arg1.isdigit():
                    i = int(arg1)
                    continue
                elif arg1 in bytecodes:
                    i = bytecodes[arg1]
                    continue
                else:
                    print(f"{i}: Invalid argument or label")
                    return

            case "JMPE" | "JMPNE" | "JMPG" | "JMPGE" | "JMPL" | "JMPLE":
                new_i = None
                if arg1 in regs:
                    if isinstance(regs[arg1], int):
                        new_i = regs[arg1]
                    else:
                        print(f"{i}: Line number must be integer")
                        return
                elif arg1.isdigit():
                    new_i = int(arg1)
                elif arg1 in bytecodes:
                    new_i = bytecodes[arg1]
                else:
                    print(f"{i}: Invalid argument or label")
                    return
                
                match opcode:
                    case "JMPE":
                        if FLAGS & E:
                            i = new_i
                            continue  
                    case "JMPNE":
                        if FLAGS & NE:
                            i = new_i
                            continue
                    case "JMPG":
                        if FLAGS & G:
                            i = new_i
                            continue
                    case "JMPGE":
                        if FLAGS & G or FLAGS & E:
                            i = new_i
                            continue
                    case "JMPL":
                        if FLAGS & L:
                            i = new_i
                            continue
                    case "JMPLE":
                        if FLAGS & L or FLAGS & E:
                            i = new_i
                            continue
            #no operation
            case "NOP":
                pass

            #print
            case "PRINT":
                if arg1 in regs:
                    print(f"{arg1} = {regs[arg1]}")
                else:
                    print(f"{i}: Invalid argument")
                    print

            case _:
                print(f"{i}: Unknown command")
                return

        i += 1
    else: #while else
        if i > max_i:
            print(f"{i}: Unknown line. Max line is {max_i - 1}")

def run(file):
    bytecodes = dict()

    if file:
        line_number = 0
        label_re = r"\s*(?P<label>\w+):"
        match = None
        label = None

        for line in file:
            match = re.search(label_re, line)
            if match:
                label = match.group('label')

                if label in bytecodes:
                    print(f"Redeclaration of label '{label}' on {line_number} line")
                    return

                bytecodes[label] = line_number
                bytecodes[line_number] = "NOP"
            else:
                bytecodes[line_number] = line.strip()
            line_number += 1
   
    handle(bytecodes, bytecodes["_start"] if "_start" in bytecodes else 0)

def main():
    file_path = input("Enter path to bytecode: ")
    
    try:
        with open(file_path, "r") as bytecode:
            run(bytecode)
    except Exception as e:
        print(e)

main()

