# percolation implemented with weighted quick union with path compression
#
class Percolation:
    # @param n : int value specifying size of grid
    def __init__(self, n):
        # n x n matrix
        self.n = n
                
        # first and last rows
        self.first_row = 1
        self.last_row = n+1
        
        # create 2 additional rows for virtual top and bottom sites
        self.grid = [[0 for c in range(n)] for r in range(n+2)]
        
        # additional storage for weighted fast union with path compression
        self.id = [x for x in range((n+2)*n)]
        self.sz = [1 for x in range((n+2)*n)]
        
        # number of components
        self.components = (n+2)*n

        # define virtual top site to be at [0,n//2]
        self.virtual_top_site = [0,n//2]
        self.virtual_top_site_id = self.gridToId(0,n//2)
        
        # define virtual bottom site to be at [n-1,n//2]
        self.virtual_bottom_site = [n+1,n//2]
        self.virtual_bottom_site_id = self.gridToId(n+1,n//2)
        
        # connect virtual top and bottom sites 
        for c in range(n):
            self.union(self.virtual_top_site_id, self.gridToId(1,c))
            self.union(self.virtual_bottom_site_id, self.gridToId(n,c))
        
    # @param row : int value of row
    # @param col : int value of col
    # @return id index of row, col
    def gridToId(self, row, col):
        return row * 10 + col
    
    # @param p : int value of id index
    # @return an int value representing the root of p
    def root(self, p):
        while p != self.id[p]:
            self.id[p] = self.id[self.id[p]] # path compression
            p = self.id[p]
        return p
    
    # @param p : int value of id index
    # @param q : int value of id index
    def union(self, p, q):
        # get the root of p and q
        root_p = self.root(p)
        root_q = self.root(q)
        
        if root_p == root_q:
            return
        
        # link root of smaller tree to the root of larger tree
        if self.sz[root_p] < self.sz[root_q]:
            self.id[root_p] = root_q
            self.sz[root_q] += self.sz[root_p]
        else:
            self.id[root_q] = root_p
            self.sz[root_p] += self.sz[root_q]
            
        # every time a union is performed we decrease the number of components by 1
        self.components -= 1
        
    # @param p : int value of id index
    # @param q : int value of id index
    # @return True if p and q are connected otherwise False
    def isConnected(self, p, q):
        return self.root(p) == self.root(q)
    
    # @return number of components
    def components(self):
        return self.components
        
    # @param row : int value of grid row
    # @param col : int value of grid col
    def open(self, row, col):
        if row < self.first_row or row >= self.last_row or col < 0 or col >= self.n:
            raise ValueError('row < self.first_row or row >= self.last_row or col < 0 or col >= self.n')
        
        self.grid[row][col] = 1
        
        dr = [ 0, 0, -1, 1]
        dc = [-1, 1,  0, 0]
        
        for rel_row, rel_col in zip(dr,dc):
            next_row = row + rel_row
            next_col = col + rel_col
            
            if next_row > 0 and next_row < self.last_row and next_col >= 0 and next_col < self.n:
                
                if self.grid[next_row][next_col] == 1:
                    p = self.gridToId(row,col)
                    q = self.gridToId(next_row,next_col)
                    self.union(p,q)
        
    # @param row : int value of grid row
    # @param col : int value of grid col
    # @return True if grid location is open otherwise False
    def isOpen(self, row, col):
        if row < self.first_row or row >= self.last_row or col < 0 or col >= self.n:
            raise ValueError('row < self.first_row or row >= self.last_row or col < 0 or col >= self.n')

        return self.grid[row][col] == 1
    
    # @param row : int value of grid row
    # @param col : int value of grid col
    # @return True if grid location can connect to virtual top site
    def isFull(self, row, col):
        if row < self.first_row or row >= self.last_row or col < 0 or col >= self.n:
            raise ValueError('row < self.first_row or row >= self.last_row or col < 0 or col >= self.n')

        # convert to Id value
        p = self.gridToId(row,col)
        
        # is grid[row][col] connected to virtual top site
        return self.isConnected(p, self.virtual_top_site_id)
    
    # @return the number of components
    def numberOfOpenSites(self):
        return self.components()
    
    # @return True if there is a connection from virtual top site to virtual bottom site
    def percolates(self):
        return self.isConnected(self.virtual_top_site_id, self.virtual_bottom_site_id)
        