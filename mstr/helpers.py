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

        # if self.leftChild is not None:
        #     t.left = self.leftChild

        self.leftChild = t

    def insertRight(self, newNode):
        if isinstance(newNode, BinaryTree):
            t = newNode
        else:
            t = BinaryTree(newNode)

        # if self.rightChild is not None:
        #     t.right = self.rightChild
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

    def inorder(self):
        if self.leftChild:
            self.leftChild.inorder()
        print(self.key)
        if self.rightChild:
            self.rightChild.inorder()

    def postorder(self):
        if self.leftChild:
            self.leftChild.postorder()
        if self.rightChild:
            self.rightChild.postorder()
        print(self.key)

    def preorder(self):
        print(self.key)
        if self.leftChild:
            self.leftChild.preorder()
        if self.rightChild:
            self.rightChild.preorder()

    def printexp(self):
        if self.leftChild:
            print('(', end=' ')
            self.leftChild.printexp()
        print(self.key, end=' ')
        if self.rightChild:
            self.rightChild.printexp()
            print(')', end=' ')

    def printtree(self, level=0):

        if self.leftChild:
            self.leftChild.printtree(level + 1)
        print("- " + str(level) + " - " + str(self.key))
        if self.rightChild:
            self.rightChild.printtree(level + 1)

    def height(self):
        return 1 + max((self.leftChild.height() if self.leftChild is not None else 0),
                       (self.rightChild.height() if self.rightChild is not None else 0))


