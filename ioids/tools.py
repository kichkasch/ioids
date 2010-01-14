"""
Tools module for IOIDS

Inter-Organisational Intrusion Detection System (IOIDS)

Check README in the IOIDS folder for more information.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import output
from sys import stdout

oneindent = ' ' * 3
SUCESS_POS = output.green('  OK  ')
SUCESS_NEG = output.red('FAILED')
SUCESS_SKIP = output.yellow(' SKIP ')
SUCESS_WARN = output.yellow('  !!  ')

COLUMN_SUCESS = 80
COLUMN_INPUT = 70
LENGTH_LINE = 89


def printAction(indent, text, linebreak = 0, out = stdout):
    """
    Prints a line for an action and puts the cursor on a predefined column.
    
    Usually, no line break is written, the line should be finished after performing an
    action using the function L{finishActionLine}.
    """
    print ((oneindent * indent) + text).ljust(COLUMN_SUCESS),
    if linebreak:
        print
    else:
        out.flush()
    
def finishActionLine(sucess = SUCESS_POS):
    """
    Finishes a line as prepared by L{printAction}.
    
    Puts the given sucess string in brackets.
    """
    print '[%s]' %(sucess)

def requestInput(indent, prompt, default = None):
    """
    Prompts the user for input.
    """
    if default:
        defaultPr = ' [%s]' %(default)
    else:
        defaultPr = ' []'
    print ((oneindent * indent) + '** ' + prompt + defaultPr).ljust(COLUMN_INPUT) + ' :',
    input = raw_input()
    if len(input) != 0:
        default = input
    return default
