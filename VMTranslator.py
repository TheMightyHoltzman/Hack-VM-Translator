import sys
import re
import os

from CodeWriter import CodeWriter
from Parser import Parser

class Main:
    fin = ''
    fout = ''
    code  = ''
    parser = ''
    codeWriter = ''

    def __init__(self, fin, fout, isTst):
        self.fin  = fin
        self.fout = fout
        self.code = ''
        self.parser     = Parser()
        # In case of a directory, this should do nothing
        fileName = self.genFilename(fin)
        self.codeWriter = CodeWriter(fileName, isTst)

    def work(self):
        fout     = open(self.fout, 'w')

        if (os.path.isdir(self.fin)):
            for file in os.listdir(self.fin):
                if file.endswith(".vm"):
                    self.parseFile(file, fout)
        else: # otherwise it is a file
            self.parseFile(self.fin, fout)

        fout.close()

    def parseFile(self, fin, fout):
        with open(fin) as f:
            lines      = f.readlines()
            for lineNr, line in enumerate(lines):
                parsed    = self.parser.parse(lineNr, line)
                assembled = self.codeWriter.write(lineNr, parsed)
                print >> fout, '//' + line
                if (assembled is not None):
                    print >> fout, assembled

    def genFilename(self, fin):
        return fin.replace('.vm', '') + '.asm'

def setup():
    if len(sys.argv) < 2:
        print 'Please provide filename or directory to parse'
        return
    fin   = sys.argv[1]

    if len(sys.argv) < 3:
        fout = fin.replace('.vm', '') + '.asm'
    else:
        fout  = sys.argv[2]

    isTst = False
    if (len(sys.argv) > 3 and sys.argv[3] == 'test'):
        isTst = True

    print  'Parsing %s into %s' % (fin,fout)

    main      = Main(fin, fout, isTst)
    main.work()

setup()
