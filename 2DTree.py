import math

class Node2D:
    def __init__(self, p):
        self.key = p
        self.left = None
        self.right = None
        self.count = 1

class Tree2D:
    def __init__(self):
        self.root = None
        
    def __size(self, node):
        if not node:
            return 0
        
        return node.count
        
    def size(self):
        return self.__size(self.root)
        
    def __insert(self, node, level, p):
        if not node:
            return Node2D(p)
        
        if level % 2 == 0:
            if p.y <= node.key.y:
                node.left = self.__insert(node.left, level+1, p)
                
            else: # p.y > node.key.y
                node.right = self.__insert(node.right, level+1, p)                
            
        else:
            if p.x <= node.key.x:
                node.left = self.__insert(node.left, level+1, p)
                
            else: # p.x > node.key.x
                node.right = self.__insert(node.right, level+1, p)
                                
        node.count = 1 + self.__size(node.left) + self.__size(node.right)
        return node
        
    def insert(self, p):
        self.root = self.__insert(self.root, 1, p)
        
    def __contains(self, node, level, p):
        if not node:
            return None
        
        if level % 2 == 0:
            if p.y < node.key.y:
                return self.__contains(node.left, level+1, p)
            
            elif p.y > node.key.y:
                return self.__contains(node.right, level+1, p)
            
            else:
                if p.x == node.key.x:
                    return node
                else:
                    return self.__contains(node.left, level+1, p)
                
        else:
            if p.x < node.key.x:
                return self.__contains(node.left, level+1, p)
            
            elif p.x > node.key.x:
                return self.__contains(node.right, level+1, p)
            
            else:
                if p.y == node.key.y:
                    return node
                else:
                    return self.__contains(node.left, level+1, p)
        
    def contains(self, p):
        if not self.root:
            return False
        
        return self.__contains(self.root, 1, p) != None
    
    def __range(self, node, level, r):
        if not node:
            return []
        
        x = []
        if r.contains(node.key):
            x.append(node.key)
            
        if level % 2 == 0:
            if r.yMin <= node.key.y and r.yMax > node.key.y:
                x += self.__range(node.left, level+1, r)
                return x + self.__range(node.right, level+1, r)
            
            elif r.yMin <= node.key.y:
                return x + self.__range(node.left, level+1, r)
            
            else:
                return x + self.__range(node.right, level+1, r)
            
        else:
            if r.xMin <= node.key.x and r.xMax > node.key.x:
                x += self.__range(node.left, level+1, r)
                return x + self.__range(node.right, level+1, r)
            
            elif r.xMin <= node.key.x:
                return x + self.__range(node.left, level+1, r)
            
            else:
                return x + self.__range(node.right, level+1, r)
        
    def range(self, r):
        return self.__range(self.root, 1, r)
    
    def __nearest(self, node, level, p):
        if not node:
            return []
        
        x = []
        x.append([node.key.distanceTo(p),node.key])
        
        if level % 2 == 0:
            if p.y <= node.key.y:
                return x + self.__nearest(node.left, level+1, p)
            
            elif p.y > node.key.y:
                return x + self.__nearest(node.right, level+1, p)
        
        else:
            if p.x <= node.key.x:
                return x + self.__nearest(node.left, level+1, p)
            
            elif p.x > node.key.x:
                return x + self.__nearest(node.right, level+1, p)
    
    def nearest(self, p):
        dist = self.__nearest(self.root, 1, p)
        nearest = dist[0]
        for i in range(1, len(dist)):
            if dist[i][0] < nearest[0]:
                nearest = dist[i]
        return nearest[1]

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distanceTo(self, p):
        # use pythagorean theorm
        dx = self.x - p.x
        dy = self.y - p.y
        z = math.sqrt(pow(dx,2)+pow(dy,2))
        return round(z,4)
    
    def __str__(self):
        return '({0},{1})'.format(self.x,self.y)
    
class RectHV:
    def __init__(self, xMin, yMin, xMax, yMax):
        self.xMin = xMin
        self.yMin = yMin
        self.xMax = xMax
        self.yMax = yMax
        
    def contains(self, p):
        if p.x >= self.xMin and p.x <= self.xMax \
            and p.y >= self.yMin and p.y <= self.yMax:
            return True
        
        return False