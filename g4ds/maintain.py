"""
User interface to g4ds for maintainence.

Grid for Digital Security (G4DS)

You may either run this module interactively or by giving parameters. Type
python maintain.py --help for more information.

@author: Michael Pilgermann
@contact: mailto:mpilgerm@glam.ac.uk
@license: GPL (General Public License)
"""

import sys
import string
import config
from maintainlib import *
    
    
NOTHING_REQUIRED = 0
FILENAME_REQUIRED = 1
ID_REQUIRED = 2

commands = {}

# general functions
commands ['s'] = ['Print status of local node', NOTHING_REQUIRED, status]
commands ['t'] = ['Send test message to node', NOTHING_REQUIRED, sendTestMessage]
commands['l'] = ['Show latest log entries', NOTHING_REQUIRED, readLog]
commands['y'] = ['Print permission matrix', NOTHING_REQUIRED, printPermissionMatrix]
commands['z'] = ['Recalculate permission matrix', NOTHING_REQUIRED, recalculatePermissions]

# member functions
commands ['i'] = ['Print information about a G4DS node', ID_REQUIRED, nodeInfo]
commands ['m'] = ['Add / update member description from file', FILENAME_REQUIRED, addMdl]
commands ['n'] = ['Export local member description to file', FILENAME_REQUIRED, getLocalMdl]
commands ['e'] = ['Add endpoints for member', NOTHING_REQUIRED, addEndpointsForMember]
commands ['p'] = ['Upload member description to remote nodes', NOTHING_REQUIRED, pushMemberDescription]

# community functions
commands['j'] = ['Print information about a Community', ID_REQUIRED, communityInfo]
commands ['c'] = ['Add / update community description from file', FILENAME_REQUIRED, addTcdl]
commands ['d'] = ['Add / update community description from remote node', NOTHING_REQUIRED, downloadAndInstallCommunityDescription]
commands['u'] = ['Subscribe member to community', NOTHING_REQUIRED, subscribeMemberToCommunity]

# service functions
commands['1'] = ['Print list of known services', NOTHING_REQUIRED, printServiceList]
commands['2'] = ['Print infomation about one service', ID_REQUIRED, printServiceInformation]
commands['3'] = ['Add / update knowledge service description from file', FILENAME_REQUIRED, addKsdl]
commands['4'] = ['Add / update knowledge service description from remote host', NOTHING_REQUIRED, downloadAndInstallKsdl]
commands['5'] = ['Push service description to remote host', NOTHING_REQUIRED, uploadKsdl]
commands['6'] = ['Subscribe member to knowledge service', NOTHING_REQUIRED, subscribeMemberToService]
commands['7'] = ['Create public key pair to connect with a client application', NOTHING_REQUIRED, createServiceKeys]

# routing functions
commands['r'] = ['Print routing table', NOTHING_REQUIRED, printRoutingTable]
commands['a'] = ['Add new route manually', NOTHING_REQUIRED, addRoute]
commands['f']  =['Flush routing table', NOTHING_REQUIRED, flushRoutingTable]
commands['w']  =['Recalculate routing table by processing gateway information', NOTHING_REQUIRED, recalculateRoutingTable]
commands['x'] = ['Poll routing information from gateways and apply to local routing table now.', NOTHING_REQUIRED, dynamicRoutingUpdate]

# options for order for order
# letter for a command
# @ for a blank line
# text for a heading or something - will be printed as given
order = [ '\tGeneral Options', 's', 't', 'l', 'y', 'z', '@', 
    '\tMember Options', 'i', 'm','n', 'e', 'p', '@', 
    '\tCommunity Options', 'j', 'c', 'd', 'u',  '@',
    '\tService Options', '1',  '2',  '3',  '4',  '5',  '6', '7', '@',
    '\tRouting Options' , 'r', 'a', 'f', 'w', 'x']

def interactive():
    global commands, order
    ch = '-1'
    while ch != 'q':
        print '\n\t\tMaintain G4DS (Node %s)' %(config.memberid)
        print '\nChoose from the following options:\n'
        for c in order:
            if c == '@':
                print
            elif commands.has_key(c):
                print '\t[%s] ... %s' %(c, commands[c][0])
            else:
                print c
        print '\n\t[q] ... Quit'
        ch = raw_input('\nChoice: ')
        ch = string.lower(ch)
        from errorhandling import G4dsRuntimeException
        try:
            if commands.has_key(ch):
                if commands[ch][1] == FILENAME_REQUIRED:
                    filename = raw_input('Enter filename: ')
                    commands[ch][2](filename)
                elif commands[ch][1] == ID_REQUIRED:
                    id = raw_input('Enter id: ')
                    commands[ch][2](id)
                else:
                    commands[ch][2]()
        except G4dsRuntimeException, msg:
            print "ERROR: %s\n" %(msg) + "=" * 89 + "\n" 
        
        if ch != 'q':
            raw_input('<hit enter to continue>')

def help():
    global commands, order
    print "Help for G4DS maintain"
    print "\nInteractive mode"
    print "Usage: python %s " %(sys.argv[0])
    print "\tAnd follow the menus."
    print "\nNon-interactive mode"
    print "Usage: \n   python %s {-s | -t | -l | -y | -z} or" %(sys.argv[0])
    print "   python %s {-i memberid | -m filename | -n filename | -e | -p} or" %(sys.argv[0])
    print "   python %s {-j communityid | -c filename | -d | -u} or" %(sys.argv[0])
    print "   python %s {-1 | -2 serviceid | -3 filename | -4 | -5 | -6 | -7} or " %(sys.argv[0])
    print "   python %s {-r |-a | -f | -w | -x}" %(sys.argv[0])
    print
    for c in order:
        if not commands.has_key(c):
            continue
        st = "\t-%s" %(c)
        if commands[c][1] == FILENAME_REQUIRED:
            st = st + " filename"
        if commands[c][1] == ID_REQUIRED:
            st = st + " id"
        st = st.ljust(15)
        st = st + " " + commands[c][0]
        print st
    
def handleArguments(args):
    import getopt
    try:
        opts, remargs = getopt.gnu_getopt(args[1:], "si:m:n:j:c:teduplrafwx12:3:4567yz", 'help')
    except getopt.GetoptError:
        help()
        return
##        sys.exit(2)        
    for opt, key in opts:
        if opt == '--help':
            help()
            break
        try:
            if commands.has_key(opt[1:]):
                command = commands[opt[1:]]
                if command[1] == FILENAME_REQUIRED:
                    filename = key
                    command[2](filename)
                elif command[1] == ID_REQUIRED:
                    id = key
                    command[2](id)
                else:
                    command[2]()
        except G4dsRuntimeException, msg:
            print "\nERROR: %s" %(msg)
    

if __name__ == "__main__":
    from g4ds import G4DS
    g = G4DS()
    g.startup()

    if len(sys.argv) == 1:
        interactive()
    else:
        handleArguments(sys.argv)
    
    g.shutdown()
