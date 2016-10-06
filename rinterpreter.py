import sys
import os

from rpython.rlib.jit import JitDriver
jitdriver = JitDriver(greens=['pc', 'program'],
                reds=['stack'])
tokens = { "ADD" : 0, "MULT" : 1, "SUB" : 2, "DIV" : 3, "JUMP" : 10,
           "JGT" : 11, "PRINT" : 12, "INT" : 13 }

def mainloop(program):
    pc = 0
    stack = Stack()
    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, stack=stack, program=program)
        command = program[pc]
        if command.has_args():
            if command.opcode == 13:
                stack.push(int(command.get_args()))
            elif command.opcode == 10:
                pc = int(command.get_args()) - 1
            elif command.opcode == 2:
                top = int(stack.pop())
                stack.push(top - int(command.get_args()))
            elif command.opcode == 3:
                top = int(stack.pop())
                stack.push(top / int(command.get_args()))
            elif command.opcode == 11:
                if stack.top > 0:
                    pc = int(command.get_args()) - 1
        else:
            if command.opcode == 0:
                stack.push(int(stack.pop()) + int(stack.pop()))
            elif command.opcode == 1:
                stack.push(int(stack.pop()) * int(stack.pop()))
            elif command.opcode == 12:
                print stack.top
        pc += 1

class Stack(object):
    def __init__(self):
        self.tail = [0]
        self.top = 0
        self.count = 0
        self.empty = True

    def push(self, value):
        if (self.empty == False):
            if (self.count == 1): self.tail[0] = self.top
            else: self.tail.append(self.top)
        else: self.empty = False
        self.count += 1
        self.top = int(value)

    def pop(self):
        if (self.empty == False):
            if (self.count == 1):
                self.empty = True
                return self.top
            else:
                head = self.top
                self.top = self.tail.pop()
                return head
            self.count -= 1
        else: return False

    def show(self):
        print self.top
        print self.tail

class Instruction(object):
    def __init__(self, opcode, args):
        self.opcode = opcode
        self.args = args

    def has_args(self):
        return (len(self.args) != 0)

    def get_args(self):
        return self.args[0]

class Instructions(object):
    def __init__(self):
        self.instructions = []
    def add_instruction(self, instruction):
        self.instructions.append(instruction)

def parse(input):
    input = input.split('\n')
    commands = Instructions()
    for line in input:
        command = line.split(' ');
        if ( command != [''] ):
            if ( len(command) == 2 ):
                instruction = Instruction(tokens[command[0]], [command[1]])
            else:
                instruction = Instruction(tokens[command[0]], [])
            commands.add_instruction(instruction)
    return commands.instructions

def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program = parse(program_contents)
    mainloop(program)

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    run(os.open(filename, os.O_RDONLY, 0777))
    return 0

def target(*args):
    return entry_point, None

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

if __name__ == "__main__":
    entry_point(sys.argv)
