class CodeWriter:

   # POINTERS - BASE ADDRESSES
   # SP   - 0
   # LCL  - 1
   # ARG  - 2
   # THIS - 3
   # THAT - 4

   # pointer 0 = THIS-POINTER (cuurent object)
   # pointer 1 = THAT-POINTER (current array)

    fileName = ''
    memMp = {
        'static': '',   # DUMMY VALUE
        'constant': '', # DUMMY VALUE
        # pointer 0 is the this pointer
        # pointer 1 is the that pointer
        'this': '3',
        'that': '4',
        'pointer': '3',
        'local': '1',
        'argument': '2',
        'temp': '5'
    }
    sp = '@SP'

    def __init__(self, fileName, isTst):
        self.isTst = isTst
        self.fileName = fileName
        if (self.isTst):
            self.sp = '@0'

    def write(self, lineNr, parsed):
        ct = parsed['commandType']
        if (ct == 'push'):
            segment = parsed['arg1']
            nr      = parsed['arg2']
            return self.push(segment, nr)
        elif (ct == 'pop'):
            segment = parsed['arg1']
            nr      = parsed['arg2']
            return self.pop(segment, nr)
        elif (ct == 'arithmetic'):
            return self.arithmetic(parsed['arg1'], lineNr)
        elif (ct == 'label'):
            return self.label(parsed['arg1']);
        elif (ct == 'goto'):
            return self.goto(parsed['arg1']);
        elif (ct == 'if'):
            return self.ifFunction(parsed['arg1']);
        elif (ct == 'function'):
            return self.function(parsed['arg1'], parsed['arg2'])
        elif (ct == 'return'):
            return self.ret();
        elif (ct == 'call'):
            return self.call(parsed['arg1'], parsed['arg2']);

    def arithmetic(self, opcode, lineNr):
        opcodeMp = {
            'add': '+',
            'sub': '-',
            'or': '|',
            'and': '&',
            'neg': '-',
            'not': '!'
        }
        jmpMp = {
            'eq': 'JEQ',
            'gt': 'JGT',
            'lt': 'JLT'
        }
        # elementary operations
        if (opcode == 'add' or opcode == 'sub' or opcode == 'or' or  opcode == 'and'):
            opSign = opcodeMp[opcode]
            # decrease stack by one
            assembled = self.sp + '\n'
            assembled += 'M=M-1' + '\n'
            # second operand in D-Register
            assembled += self.sp + '\n'
            assembled += 'A=M' + '\n'
            assembled += 'D=M' + '\n'
            # first in M-Register
            assembled += self.sp + '\n'
            assembled += 'A=M-1' + '\n'
            # ... and operate
            assembled += 'M=M' + opSign + 'D' + '\n'
        # not (unitary) operator
        elif (opcode == 'not' or opcode == 'neg'):
            opSign = opcodeMp[opcode]
            # get first
            assembled = self.sp + '\n'
            # ... and operate
            assembled += 'A=M-1' + '\n'
            assembled += 'M=' + opSign + 'M' + '\n'
        # comparisons: eq, gt, lt
        else:
            jpSign = jmpMp[opcode]
            endLbl = 'end' + str(lineNr)
            ifLbl  = 'yes' + str(lineNr)
            # decrease stack by one
            assembled = self.sp + '\n'
            assembled += 'M=M-1' + '\n'
            # second operand in D-Register
            assembled += self.sp + '\n'
            assembled += 'A=M' + '\n'
            assembled += 'D=M' + '\n'
            # first in M-Register
            assembled += self.sp + '\n'
            assembled += 'A=M-1' + '\n'
            # ... compare
            assembled += 'D=M-D;' + '\n'
            # ... jump if true
            assembled += '@' + ifLbl + '\n'
            assembled += 'D;' + jpSign + '\n'
            # ... false branch
            assembled += '@0' + '\n'
            assembled += 'D=A' + '\n'
            assembled += self.sp + '\n'
            assembled += 'A=M-1' + '\n'
            assembled += 'M=D' + '\n'
            assembled += '@' + endLbl + '\n'
            assembled += '0;JMP' + '\n'
            # ... true branch
            assembled +=  '(' + ifLbl + ')' + '\n'
            assembled += '@1' + '\n'
            assembled += 'D=D-A' + '\n'
            assembled += self.sp + '\n'
            assembled += 'A=M-1' + '\n'
            assembled += 'M=D' + '\n'
            # endlabel
            assembled += '(' + endLbl + ')\n'

        return assembled

    def push(self, segment, nr):
        sgmtMpd = self.memMp[segment]

        if(segment == 'constant'):
            assembled = '@' + nr + '\n'
            assembled += 'D=A' + '\n'
            assembled += self.sp + '\n'
            assembled += 'A=M' + '\n'
            assembled += 'M=D' + '\n'
            # advance stack pointer by one ...
            assembled += self.sp + '\n'
            assembled += 'M=M+1' + '\n'

            return assembled

        elif(segment == 'pointer'):
            # *SP=THIS/THAT, SP++
            ptr = int(nr) + 3
            assembled = '@' + str(ptr) + '\n'
            assembled += 'D=M' + '\n'
            assembled += self.sp + '\n'
            assembled += 'A=M' + '\n'
            assembled += 'M=D' + '\n'
            # advance stack pointer by one ...
            assembled += self.sp + '\n'
            assembled += 'M=M+1' + '\n'
            return assembled

        if(segment == 'static'):
            # create a label
            lbl = self.fileName.split("/")[-1] + "." +  nr
            assembled = '@' + lbl + '\n'
            assembled += 'D=M' + '\n'
        elif (segment == 'temp'):
            # base address + nr ...
            assembled = '@5' + '\n'
            assembled += 'D=A' + '\n'
            assembled += '@' + nr + '\n'
            assembled += 'A=A+D' + '\n'
            assembled += 'D=M' + '\n'
        else:
            # base address + nr ...
            assembled = '@' + sgmtMpd + '\n'
            assembled += 'D=M' + '\n'
            assembled += '@' + nr + '\n'
            assembled += 'A=A+D' + '\n'
            assembled += 'D=M' + '\n'
        # put it on the stack
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'
        # advance stack pointer by one ...
        assembled += self.sp + '\n'
        assembled += 'M=M+1' + '\n'

        return assembled

    def pop(self, segment, nr):
        # decrease stack by one
        assembled = self.sp + '\n'
        assembled += 'M=M-1' + '\n'
        if(segment == 'static'):
            # create a label
            lbl = self.fileName.split("/")[-1] + '.' +  nr + '\n'
            # get topmost value from stack
            assembled += 'A=M' + '\n'
            assembled += 'D=M' + '\n'
            # and put it into labelled address
            assembled += '@' + lbl + '\n'
            assembled += 'M=D' + '\n'

            return assembled

        elif(segment == 'pointer'):
            # SP--,THIS/THAT=*SP
            ptr = int(nr) + 3
            assembled += 'A=M' + '\n'
            assembled += 'D=M' + '\n'
            assembled += '@' + str(ptr) + '\n'
            assembled += 'M=D'
            return assembled

        elif(segment == 'temp'):
            # build address and put into D-register ...
            assembled += '@5' + '\n'
            assembled += 'D=A' + '\n'
            assembled += '@' + nr + '\n'
            assembled += 'D=A+D' + '\n'
        else:
            # build address and put into D-register ...
            sgmtMpd = self.memMp[segment]
            assembled += '@' + sgmtMpd + '\n'
            assembled += 'D=M' + '\n'
            assembled += '@' + nr + '\n'
            assembled += 'D=A+D' + '\n'
        assembled += '@R13' + '\n'
        assembled += 'M=D' + '\n'
        # get topmost value from stack
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        # and put into built address
        assembled += '@R13' + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'

        return assembled

    def label(self, lbl):
        return '(' + lbl + ')' + '\n'

    def goto(self, lbl):
        assembled = '@' + lbl + '\n'
        assembled += '0;JMP' + '\n'
        return assembled

    def ifFunction(self, lbl):
        assembled = self.sp + '\n'
        assembled = 'A=M' + '\n'
        assembled += 'D=M' + '\n' # put value of the stack pointer into D
        assembled += '@' + lbl + '\n'
        assembled += 'D=D;JNE'
        return assembled

    def function(self, lbl, nrArgs):
        assembled = '(' + lbl + ')'
        while(int(nrArgs) > 0):
            assembled += self.push('constant', 0)
        return assembled

    def ret(self):
        # todo
        return ''

    def call(self, lbl, nArgs):
        assembled  = ''
        #  In the course of implementing the code of f
        # (the caller), we arrive to the command call g nArgs.
        # we assume that nArgs arguments have been pushed
        # onto the stack. What do we do next?
        # Next, we effect the following logic:
        #push returnAddress # saves the return address

        # push LCL # saves the LCL of f
        assembled += '@LCL' + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'
        assembled += self.sp + '\n'
        assembled += 'M=M+1' + '\n'

        #push ARG # saves the ARG of f
        assembled += '@ARG' + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'
        assembled += self.sp + '\n'
        assembled += 'M=M+1' + '\n'

        #push THIS # saves the THIS of f
        assembled += '@THIS' + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'
        assembled += self.sp + '\n'
        assembled += 'M=M+1' + '\n'

        #push THAT # saves the THAT of f
        assembled += '@THAT' + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'M=D' + '\n'
        assembled += self.sp + '\n'
        assembled += 'M=M+1' + '\n'

        # ARG = SP-nArgs-5 # repositions SP for g
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += '@' + int(nrArgs) + '\n'
        assembled += 'D=D-A' + '\n'
        assembled += '@5' + '\n'
        assembled += 'D=D-A' + '\n'
        assembled += '@ARG' + '\n'
        assembled += 'M=D' + '\n'

        # LCL = SP # repositions LCL for g
        assembled += self.sp + '\n'
        assembled += 'A=M' + '\n'
        assembled += 'D=M' + '\n'
        assembled += '@LCL' + '\n'
        assembled += 'M=D' + '\n'

        #goto g # transfers control to g
        assembled += self.goto(lbl);

        # todo
        #returnAddress: # the generated symbol

        return assembled
