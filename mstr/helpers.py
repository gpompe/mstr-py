class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self) -> object:
        return self.items.pop()

    def lookback(self, n=1):
        if len(self.items) - n < 0:
            return None
        else:
            return self.items[len(self.items) - n]

    def size(self):
        return len(self.items)


class BinaryTree:
    """
    A recursive implementation of Binary Tree
    Using links and Nodes approach.
    Modified to allow for trees to be constructed from other trees rather than always creating
    a new tree in the insertLeft or insertRight
    """

    def __init__(self, rootObj):
        self.key = rootObj
        self.leftChild = None
        self.rightChild = None

    def insertLeft(self, newNode):

        if isinstance(newNode, BinaryTree):
            t = newNode
        else:
            t = BinaryTree(newNode)

        self.leftChild = t

    def insertRight(self, newNode):
        if isinstance(newNode, BinaryTree):
            t = newNode
        else:
            t = BinaryTree(newNode)

        self.rightChild = t

    def isLeaf(self):
        return (not self.leftChild) and (not self.rightChild)

    def getRightChild(self):
        return self.rightChild

    def getLeftChild(self):
        return self.leftChild

    def setRootVal(self, obj):
        self.key = obj

    def getRootVal(self, ):
        return self.key


    def todict(self):
        if self.isLeaf():
            return self.key.todict()
        else:
            operands = []
            if self.leftChild is not None:
                operands.append(self.leftChild.todict())
            if self.rightChild is not None:
                operands.append(self.rightChild.todict())
            return dict(operator=self.key, operands=operands)




