# The Board class inherits from this interface, so that we
# don't need to add any special logic in the BinaryHeap 
# class to get the Board value used for the min heap
# comparisons.
import abc
class CompareInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, '__gt__') and callable(subclass.__gt__) \
                and hasattr(subclass, '__le__') and callable(subclass.__le__)
    
    @abc.abstractmethod
    def __gt__(self, right):
        raise NotImplementedError
    
    @abc.abstractmethod
    def __le__(self, right):
        raise NotImplementedError
    

# Priority queue implemented using a binary heap.
# The binary heap is represented with an array.
# Array element 0 is ignored. First element starts
# at element 1, which means our calculation for 
# child elements is 2K and 2K+1 for left and right
# child respectively. The parent of K is K//2.
# Also, this is min heap.  We are using a min heap
# because we want the smallest manhattan value at
# the root.  This will allow us to find the next
# move that will get us to our goal
class BinaryHeap:
    def __init__(self):
        self.heap = [0]
        self.N = 0
    
    def __swim(self, k):            
        while k > 1 and self.heap[k//2] > self.heap[k]:
            temp = self.heap[k//2]
            self.heap[k//2] = self.heap[k]
            self.heap[k] = temp
            
            k = k//2
            
    def __sink(self, k):
        while 2*k <= self.N:
            j = 2*k
            if j < self.N and self.heap[j] > self.heap[j+1]:
                j += 1
            if self.heap[k] <= self.heap[j]:
                break
            
            temp = self.heap[k]
            self.heap[k] = self.heap[j]
            self.heap[j] = temp
            
            k = j
            
    def insert(self, item):
        # ensure that the input parameter inherits from CompareInterface
        if not issubclass(type(item), CompareInterface):
            raise ValueError('item must inherit from the CompareInterface')

        self.N += 1
        self.heap.append(item)
        self.__swim(self.N)
        
    def delMin(self):
        minKey = self.heap[1]     
        self.heap[1] = self.heap[self.N]
        self.N -= 1
        
        self.__sink(1)
        del self.heap[self.N+1]
        
        return minKey
    

class Board(CompareInterface):
    def __init__(self, board):
        self.board = board
        self.N = len(board)
        
        self.hamming_dist = -1
        self.manhattan_dist = -1
        
        # map expected tile to position
        self.tileToPos = {}
        counter = 1
        for r in range(self.N):
            for c in range(self.N):
                self.tileToPos[counter] = [r,c]
                counter += 1
        self.tileToPos[self.N*self.N] = 0
        
    def __str__(self):
        board = ''
        
        for r in range(self.N):
            for c in range(self.N):
                board += '%s ' % self.board[r][c]
            board += '\n'
            
        return board
    
    def __len__(self):
        return self.N
    
    def __eq__(self, board):
        if self.N != len(board):
            return False
        
        for r in range(self.N):
            for c in range(self.N):
                if self.board[r][c] != board.board[r][c]:
                    return False
        
        return True
    
    def __gt__(self, board):
        if self.manhattan_dist == -1:
            self.manhattan_dist = self.manhattan()
            
        if self.manhattan_dist > board.manhattan():
            return True
        
        return False
    
    def __le__(self, board):
        if self.manhattan_dist == -1:
            self.manhattan_dist = self.manhattan()
            
        if self.manhattan_dist <= board.manhattan():
            return True
        
        return False
    
    def hamming(self):
        hamming_dist = 0
        
        for r in range(self.N):
            for c in range(self.N):
                expected = (r+2*r) + (c+1)
                if self.board[r][c] != expected:
                    hamming_dist += 1
        
        # decrement because we don't want to count 0
        self.hamming_dist = hamming_dist-1
        return hamming_dist-1
    
    def manhattan(self):
        manhattan_dist = 0
                
        for r in range(self.N):
            for c in range(self.N):
                # find distance of current element to its correct position
                val = self.board[r][c]
                if val != 0:
                    pos = self.tileToPos[val]
                    dist = abs(r-pos[0]) + abs(c-pos[1])
                    manhattan_dist += dist
        
        self.manhattan_dist = manhattan_dist
        return manhattan_dist
    
    def isGoal(self):
        for r in range(self.N):
            for c in range(self.N):
                if not (r == self.N-1 and c == self.N-1):
                    expected = (r+2*r) + (c+1)
                    if self.board[r][c] != expected:
                        #print('Expected %d at (%d,%d) but got %d' % (expected,r,c,self.board[r][c]))
                        return False
        
        return True
    
    def neighbors(self):
        neighbors = []
        pos0 = []
        
        # find tile 0
        for r in range(self.N):
            for c in range(self.N):
                if self.board[r][c] == 0:
                    pos0 = [r,c]
                    break
            if pos0:
                break
                
        dr = [ 0, 0, -1, 1]
        dc = [-1, 1,  0, 0]
        
        for next_rel_pos in zip(dr,dc):
            next_row = pos0[0] + next_rel_pos[0]
            next_col = pos0[1] + next_rel_pos[1]
            
            if next_row >= 0 and next_row < self.N and next_col >= 0 and next_col < self.N:
                # copy the board and update it
                n = [[0 for c in range(self.N)] for r in range(self.N)]
                for r in range(self.N):
                    for c in range(self.N):
                        n[r][c] = self.board[r][c]
                        
                n[next_row][next_col] = 0
                n[pos0[0]][pos0[1]] = self.board[next_row][next_col]
                neighbors.append(Board(n))
                
        return neighbors
    

class Solver:
    def __init__(self, board):
        self.board = board
        
    def isSolvable(self):
        board = self.board
        binaryHeap = BinaryHeap()
        binaryHeap.insert(board)
        
        if board.isGoal():
            return True
        
        hammingDistCount = 0
        hammingCountThreshold = len(board)*10000
                
        while not board.isGoal() and hammingDistCount < hammingCountThreshold:
            neighborBoards = board.neighbors()
            
            for nb in neighborBoards:
                if nb != board:
                    binaryHeap.insert(nb)
            
            board = binaryHeap.delMin()
            
            if board.hamming() >= 2:
                hammingDistCount += 1
            print(board.hamming(), hammingDistCount)
                        
        return (True if hammingDistCount < hammingCountThreshold else False)
        
    def moves(self):
        # minimum number of moves to solve the initial board; -1 if unsolvable
        moves = 0
        
        board = self.board
        binaryHeap = BinaryHeap()
        binaryHeap.insert(board)
        
        if board.isGoal():
            return 0
        
        if not self.isSolvable():
            return -1
        
        while not board.isGoal():
            neighborBoards = board.neighbors()
            
            for nb in neighborBoards:
                if nb != board:
                    binaryHeap.insert(nb)
                    
            board = binaryHeap.delMin()
            moves += 1
        
        return moves
        
    def solution(self):
        # sequence of boards in a shortest solution; null if unsolvable      
        ret = []
        
        board = self.board
        binaryHeap = BinaryHeap()
        binaryHeap.insert(board)
        
        ret.append(board)
        
        if board.isGoal():
            return ret
        
        if not self.isSolvable():
            return []
                
        while not board.isGoal():
            neighborBoards = board.neighbors()
            
            for nb in neighborBoards:
                if nb != board:
                    binaryHeap.insert(nb)
            
            board = binaryHeap.delMin()
            ret.append(board)
        
        return ret
    
b = [
    [0,1,3],
    [4,2,5],
    [7,8,6]
]
solver = Solver(Board(b))
for board in solver.solution():
    print(board)
solver.moves()
