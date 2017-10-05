import sys
import re
import os

class Parser:

    C_ARITHMETIC = 'arithmetic' # add|sub|neq|eq|gt|lt|and|or|not
    C_PUSH       = 'push'
    C_POP        = 'pop'
    C_LABEL      = 'label'
    C_GOTO       = 'goto'
    C_IF         = 'if-goto'
    C_FUNCTION   = 'function'
    C_RETURN     = 'return'
    C_CALL       = 'call'

    def printAll(self, dict):
        for key, value in dict.items():
            print('%s -> %s') % (key, value)

    def parse(self, nr, line):
        lineStrip = line.strip()
        lineStrip = re.sub('\s+', ' ', lineStrip) # multiple spaces by single space

        if (lineStrip == ''):
            return {'commandType': 'empty'}
        # COMMENTS

        elif (lineStrip.startswith('//') or (not lineStrip)):
            return {'commandType': 'comment'}

        elif (lineStrip.startswith('push') or lineStrip.startswith('pop') or lineStrip.startswith('function') or lineStrip.startswith('call')):
            split = lineStrip.split(' ')
            return {'commandType': split[0], 'arg1': split[1], 'arg2': split[2]}

        elif (lineStrip == 'add' or lineStrip == 'sub' or lineStrip == 'neg' or lineStrip == 'eq' or lineStrip == 'gt' or lineStrip == 'lt' or lineStrip == 'and' or lineStrip == 'or' or lineStrip == 'not'):
            return {'commandType': 'arithmetic', 'arg1': lineStrip}

        elif (lineStrip.startswith('goto')):
            split = lineStrip.split(' ')
            return {'commandType': 'goto', 'arg1': split[1]}

        elif (lineStrip.startswith('label')):
            split = lineStrip.split(' ')
            return {'commandType': 'label', 'arg1': split[1]}

        elif (lineStrip.startswith('if')):
            split = lineStrip.split(' ')
            return {'commandType': 'if', 'arg1': split[1]}

        elif (lineStrip.startswith('function')):
            split = lineStrip.split(' ')
            return {'commandType': 'function', 'arg1': split[1], 'arg2': split[2]}

        elif (lineStrip.startswith('return')):
            return {'commandType': 'return'}

        elif (lineStrip.startswith('call')):
            return {'commandType': 'call', 'arg1': split[1], 'arg2': split[2]}
