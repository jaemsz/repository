# left leaning red-black tree
#
class RBNode:
    RED = True
    BLACK = False
    
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.left = None
        self.right = None
        self.color = RBNode.RED
        self.count = 1
        
class RBTree:
    class RBTreeIterator:
        def __init__(self, redBlackTree):
            self.curr = redBlackTree.root
            self.stack = []
            self.fillStack()
            
        def fillStack(self):
            while self.curr:
                self.stack.append(self.curr)
                self.curr = self.curr.left
                
        def __next__(self):
            if self.stack:
                item = self.stack.pop()
                self.curr = item.right
                self.fillStack()
                
                return item.key, item.val, item.count

            raise StopIteration
            
    def __init__(self):
        self.root = None
    
    def __rotateLeft(self, node):
        temp = node.right
        node.right = temp.left
        temp.left = node
        
        temp.color = node.color
        node.color = RBNode.RED
        
        return temp
    
    def __rotateRight(self, node):
        temp = node.left
        node.left = temp.right
        temp.right = node
        
        temp.color = node.color
        node.color = RBNode.RED
        
        return temp
    
    def __flipColors(self, node):
        node.color = RBNode.RED
        node.left.color = RBNode.BLACK
        node.right.color = RBNode.BLACK
        
    def __isRed(self, node):
        if not node:
            return False
        
        return node.color == RBNode.RED
    
    def __size(self, node):
        if not node:
            return 0
        
        return node.count
    
    def size(self):
        if not self.root:
            return 0
        
        return self.__size(self.root)
        
    def __put(self, node, key, val):
        if not node:
            return RBNode(key, val)
        
        if key < node.key:
            node.left = self.__put(node.left, key, val)
            
        elif key > node.key:
            node.right = self.__put(node.right, key, val)
            
        else:
            node.val = val
            
        if self.__isRed(node.right) and not self.__isRed(node.left):
            # This is a fix for a bug in Robert Sedgewick's lecture notes
            tnode = self.__rotateLeft(node)
            node.count = (1 + self.__size(node.left) + self.__size(node.right))
            node = tnode
        
        if self.__isRed(node.left) and self.__isRed(node.left.left):
            # This is a fix for a bug in Robert Sedgewick's lecture notes
            tnode = self.__rotateRight(node)
            node.count = (1 + self.__size(node.left) + self.__size(node.right))
            node = tnode
            
        if self.__isRed(node.left) and self.__isRed(node.right):
            self.__flipColors(node)
        
        node.count = (1 + self.__size(node.left) + self.__size(node.right))
        return node
        
    def put(self, key, val):
        self.root = self.__put(self.root, key, val)
        
    def get(self, key):
        currNode = self.root
        
        while currNode:
            if key < currNode.key:
                currNode = currNode.left
                
            elif key > currNode.key:
                currNode = currNode.right
                
            else:
                return currNode.val
            
        return None
    
    def min(self):
        currNode = self.root
        
        while currNode.left:
            currNode = currNode.left
            
        return currNode.val
    
    def max(self):
        currNode = self.root
        
        while currNode.right:
            currNode = currNode.right
            
        return currNode.val
    
    def __floor(self, node, key):
        if not node:
            return None
        
        if key == node.key:
            return node
        
        elif key < node.key:
            return self.__floor(node.left, key)
        
        else:
            t = self.__floor(node.right, key)
            return t if t else node
        
    def floor(self, key):
        node = self.__floor(self.root, key)
        
        if not node:
            return None
        
        return node.key
    
    def __ceiling(self, node, key):
        if not node:
            return None
        
        if key == node.key:
            return node
        
        elif key > node.key:
            return self.__ceiling(node.right, key)
            
        else:
            t = self.__ceiling(node.left, key)
            return t if t else node
        
    def ceiling(self, key):
        node = self.__ceiling(self.root, key)
        
        if not node:
            return None
        
        return node.key
    
    def __rank(self, node, key):
        if not node:
            return 0
        
        if key < node.key:
            return self.__rank(node.left, key)
        
        elif key > node.key:
            return (1 + self.__size(node.left) + self.__rank(node.right, key))
        
        else:
            return self.__size(node.left)
    
    def rank(self, key):
        return self.__rank(self.root, key)
    
    def rangeCount(self, loKey, hiKey):
        hiKeyVal = self.get(hiKey)
        
        if hiKeyVal is not None:
            return (self.rank(hiKey) - self.rank(loKey) + 1)
        
        else:
            return (self.rank(hiKey) - self.rank(loKey))
    
    def __iter__(self):
        return self.RBTreeIterator(self)
    

bst = RBTree()

import random
random.seed(17)
keys = []
for i in random.sample(range(1000),20):
    keys.append(i)
    bst.put(i,i)
