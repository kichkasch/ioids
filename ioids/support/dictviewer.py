import wx, wx.gizmos

class Tree(wx.gizmos.TreeListCtrl):

    def _addItemsNow(self, parentTreeNode, content):
        item = self.AppendItem(parentTreeNode, '')
        self.SetItemText(item, content[0])
        i = 1
        for attName in content[1].keys():
            attValue = content[1][attName]
            self.SetItemText(item, "%s (%s)" %(attValue, attName), i)
            i += 1
        
        for rel in content[2]:
            self._addItemsNow(item, rel)

    def __init__(self, parent, content = []):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, style=wx.TR_DEFAULT_STYLE)
        
        self.AddColumn('Node name')
        for x in range(1,10):
            self.AddColumn('Att %d' %(x))
        
        self._addItemsNow(self.GetRootItem(), content)

def showNow(content):
    app = wx.PySimpleApp()
    frm = wx.Frame(None, -1, 'TreeListCtrlTestApp')
    tlc = Tree(frm, content)
    frm.Show(1)
    app.MainLoop()
    
ONE_SPACE = '    '
class AsciiTree:
    def _oneNode(self, node, indent):
        print ONE_SPACE  * indent + str(node[0])
        for rel in node[2]:
            self._oneNode(rel, indent + 1)
    
    def __init__(self, content):
        self._oneNode(content, 0)
    
def showNowAscii(content):
    tree = AsciiTree(content)
    
if __name__ == '__main__':
    dictAddress = {}
    dictAddress['street'] = '18 Llandough Street'
    dictAddress['town'] = 'Cardiff'
    
    dict = {}
    dict['name'] = 'Michael'
    showNow(['person',dict, [['address',dictAddress, []]]])
