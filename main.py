import re

class VirtualMachine:
    
    def __init__(self):
        self.REGS = {
            "AX" : 0,
            "BX" : 0,
            "CX" : 0,
            "DX" : 0,
            "SP" : -1,
            "BP" : 0,
        }
        self.IP = 0
        
        self.FLAGS = 0 #E NE G L
        self.E = 1
        self.NE = 2
        self.G = 4
        self.L = 8
        
        self.STACK = []
        
        self.command_re = r"\s*(?P<opcode>[A-Z]+)\s?(?P<arg1>[a-zA-z0-9_\-.]+)?,?\s?(?P<arg2>[a-zA-z0-9_\-.]+)?$"


    def run(self, bytecodes, ip = 0):
        self.IP = ip
        
        max_IP = 0
        for key in bytecodes.keys():
            if isinstance(key, int):
                max_IP += 1

        while self.IP < max_IP:
            if self.IP not in bytecodes:
                print(f"{self.IP}: Unknown line")
                return

            if bytecodes[self.IP] == "":
                self.IP += 1
                continue

            match = re.search(self.command_re, bytecodes[self.IP])
            
            if match is None:
                print(f"{self.IP}: Unknown command")
                return

            opcode = match.group('opcode')
            arg1 = match.group('arg1')
            arg2 = match.group('arg2')

            match opcode:
                case "MOV":
                    if arg1 in self.REGS:
                        if arg2 in self.REGS:
                            self.REGS[arg1] = self.REGS[arg2]
                        elif self.is_number(arg2):
                            self.REGS[arg1] = self.to_number(arg2)
                        else:
                            print(f"{self.IP}: Invalid second argument")
                            return
                    else:
                        print(f"{self.IP}: Invalid first argument")
                        return
                
                #arithmetic operations
                case "ADD": 
                    if arg1 in self.REGS:
                        if arg2 in self.REGS:
                            self.REGS[arg1] = self.REGS[arg1] + self.REGS[arg2]
                        elif self.is_number(arg2):
                            self.REGS[arg1] = self.REGS[arg1] + self.to_number(arg2)
                        else:
                            print(f"{self.IP}: Invalid second argument")
                            return
                    else:
                        print(f"{self.IP}: Invalid first argument")
                        return

                case "SUB": 
                    if arg1 in self.REGS:
                        if arg2 in self.REGS:
                            self.REGS[arg1] = self.REGS[arg1] - self.REGS[arg2]
                        elif self.is_number(arg2):
                            self.REGS[arg1] = self.REGS[arg1] - self.to_number(arg2)
                        else:
                            print(f"{self.IP}: Invalid second argument")
                            return
                    else:
                        print(f"{self.IP}: Invalid first argument")
                        return
                
                case "MULT": 
                    if arg1 in self.REGS:
                        if arg2 in self.REGS:
                            self.REGS["DX"] = self.REGS[arg1] * self.REGS[arg2]
                        elif self.is_number(arg2):
                            self.REGS["DX"] = self.REGS[arg1] * self.to_number(arg2)
                        else:
                            print(f"{self.IP}: Invalid second argument")
                            return
                    else:
                        print(f"{self.IP}: Invalid first argument")
                        return
                
                case "DIV": 
                    if arg1 in self.REGS:
                        if arg2 in self.REGS:
                            self.REGS["DX"] = self.REGS[arg1] / self.REGS[arg2]
                        elif self.is_number(arg2):
                            self.REGS["DX"] = self.REGS[arg1] / self.to_number(arg2)
                        else:
                            print(f"{self.IP}: Invalid second argument")
                            return
                    else:
                        print(f"{self.IP}: Invalid first argument")
                        return
                
                #stack operations
                case "PUSH":
                    if arg1 in self.REGS:
                        self.REGS["SP"] += 1
                        self.STACK.append( self.REGS[arg1] )
                    elif self.is_number(arg1):
                        self.REGS["SP"] += 1
                        self.STACK.append( self.to_number(arg1) )
                    else:
                        print(f"{self.IP}: Invalid argument")
                        return

                case "POP":
                    if arg1 in self.REGS:
                        if self.REGS["SP"] < 0:
                            print(f"{self.IP}: Stack is empty")
                            return
                            
                        elif self.REGS["SP"] < self.REGS["BP"]:
                            print(f"{self.IP}: You went out of your stack frame")
                            return
                            
                        self.REGS["SP"] -= 1
                        self.REGS[arg1] = self.STACK.pop()
                    else:
                        print(f"{self.IP}: Invalid argument")
                        return
              
                #call operations 
                case "CALL":
                    if arg1 in self.REGS:
                        if isinstance(self.REGS[arg1], int):
                            self.REGS["SP"] += 1
                            self.STACK.append(self.IP + 1)
                            self.IP = self.REGS[arg1]
                            continue
                        else:
                            print(f"{self.IP}: Line number must be integer")
                            return
                    elif arg1.isdigit():
                        self.REGS["SP"] += 1
                        self.STACK.append(self.IP + 1)
                        self.IP = int(arg1)
                        continue
                    elif arg1 in bytecodes:
                        self.REGS["SP"] += 1
                        self.STACK.append(self.IP + 1)
                        self.IP = bytecodes[arg1]
                        continue
                    else:
                        print(f"{self.IP}: Invalid argument or label")
                        return

                case "CLEARF":
                    diff = self.REGS["SP"] - self.REGS["BP"]
                    if diff < 0:
                        print(f"{self.IP}: SP is lower than BP")
                        return
                    elif diff > 0:
                        self.REGS["SP"] = self.REGS["BP"]
                        try:
                            del self.STACK[self.REGS["BP"] + 1:]
                        except Exception as e:
                            print(f"{self.IP}: Can not clear stack frame because {e}")

                case "RET":
                    if self.REGS["SP"] < 0:
                        print(f"{self.IP}: Stack is empty")
                        return
                            
                    elif self.REGS["SP"] < self.REGS["BP"]:
                        print(f"{self.IP}: You did not restore BP")
                        return
                            
                    self.REGS["SP"] -= 1
                    self.IP = self.STACK.pop()
                    continue

                case "PRINTSTACK":
                    print(self.STACK)

                #compare
                case "CMP":
                    left = None
                    right = None
                    if arg1 in self.REGS and arg2 in self.REGS:
                        left = self.REGS[arg1]
                        right = self.REGS[arg2]
                    elif arg1 in self.REGS and self.is_number(arg2):
                        left = self.REGS[arg1]
                        right = self.to_number(arg2)
                    elif self.is_number(arg1) and arg2 in self.REGS:
                        left = self.to_number(arg1)
                        right = self.REGS[arg2]
                    elif self.is_number(arg1) and self.is_number(arg2):
                        left = self.to_number(arg1)
                        right = self.to_number(arg2)
                    else:
                        print(f"{self.IP}: Ivalid first/second/both argument(s)")
                        return

                    self.FLAGS = 0
                    if left == right:
                        self.FLAGS |= self.E
                    elif left < right:
                        self.FLAGS |= self.L
                        self.FLAGS |= self.NE
                    elif left > right:
                        self.FLAGS |= self.G
                        self.FLAGS |= self.NE

                #jumps
                case "JMP":
                    if arg1 in self.REGS:
                        if isinstance(self.REGS[arg1], int):
                            self.IP = self.REGS[arg1]
                            continue
                        else:
                            print(f"{self.IP}: Line number must be integer")
                            return
                    elif arg1.isdigit():
                        self.IP = int(arg1)
                        continue
                    elif arg1 in bytecodes:
                        self.IP = bytecodes[arg1]
                        continue
                    else:
                        print(f"{self.IP}: Invalid argument or label")
                        return

                case "JMPE" | "JMPNE" | "JMPG" | "JMPGE" | "JMPL" | "JMPLE":
                    new_IP = None
                    if arg1 in self.REGS:
                        if isinstance(self.REGS[arg1], int):
                            new_IP = self.REGS[arg1]
                        else:
                            print(f"{self.IP}: Line number must be integer")
                            return
                    elif arg1.isdigit():
                        new_IP = int(arg1)
                    elif arg1 in bytecodes:
                        new_IP = bytecodes[arg1]
                    else:
                        print(f"{self.IP}: Invalid argument or label")
                        return
                    
                    match opcode:
                        case "JMPE":
                            if self.FLAGS & self.E:
                                self.IP = new_IP
                                continue  
                        case "JMPNE":
                            if self.FLAGS & self.NE:
                                self.IP = new_IP
                                continue
                        case "JMPG":
                            if self.FLAGS & self.G:
                                self.IP = new_IP
                                continue
                        case "JMPGE":
                            if self.FLAGS & self.G or self.FLAGS & self.E:
                                self.IP = new_IP
                                continue
                        case "JMPL":
                            if self.FLAGS & self.L:
                                self.IP = new_IP
                                continue
                        case "JMPLE":
                            if self.FLAGS & self.L or self.FLAGS & self.E:
                                self.IP = new_IP
                                continue
                #no operation
                case "NOP":
                    pass

                #print
                case "PRINT":
                    if arg1 in self.REGS:
                        print(f"{arg1} = {self.REGS[arg1]}")
                    else:
                        print(f"{self.IP}: Invalid argument")
                        print

                case _:
                    print(f"{self.IP}: Unknown command")
                    return

            self.IP += 1
        else: #while else
            if self.IP > max_IP:
                print(f"{self.IP}: Unknown line. Max line is {max_IP - 1}")
            

    def load(self, file):
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
       
            self.run(bytecodes, bytecodes["_start"] if "_start" in bytecodes else 0)
        else:
            print("Some error with during loading file to VirtualMachine")
    
    
    def to_number(self, s):
        if s in ["-", ".", "-."]:
            return float(0)
        else:
            return float(s) 


    def is_number(self, s):
        if not s:
            return False
        num_re = r"-?\d*\.?\d*"
        match = re.match(num_re, s)
        return s == match.group()


def main():
    file_path = input("Enter path to file with bytecode: ")
    vm = VirtualMachine()
    
    try:
        with open(file_path, "r") as file:
            vm.load(file)
    except Exception as e:
        print(e)

main()
