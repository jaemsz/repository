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
        
        # number of open sites
        self.openSiteCount = 0

        # number of components
        self.componentsCount = n*n+2

        # create 2 additional rows for virtual top and bottom sites
        self.grid = []
        self.grid.append([0])
        for r in range(n):
            self.grid.append([0 for j in range(n)])
        self.grid.append([0])
        
        # additional storage for weighted fast union with path compression
        self.id = [x for x in range(n*n+2)]
        self.sz = [1 for x in range(n*n+2)]

        # define virtual top site to be at [0,0]
        self.virtual_top_site_id = self.__gridToId(0,0)
                                    
        # define virtual bottom site to be at [n+1,0]
        self.virtual_bottom_site_id = self.__gridToId(n+1,0)
        
        # connect virtual top and bottom sites 
        for c in range(n):
            self.__union(self.virtual_top_site_id, self.__gridToId(1,c))
            self.__union(self.virtual_bottom_site_id, self.__gridToId(n,c))
    
    # @param p : int value of id index
    # @return an int value representing the root of p
    def __root(self, p):
        while p != self.id[p]:
            self.id[p] = self.id[self.id[p]] # path compression
            p = self.id[p]
        return p
    
    # @param p : int value of id index
    # @param q : int value of id index
    def __union(self, p, q):
        # get the root of p and q
        root_p = self.__root(p)
        root_q = self.__root(q)
        
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
        self.componentsCount -= 1
        
    # @param p : int value of id index
    # @param q : int value of id index
    # @return True if p and q are connected otherwise False
    def __isConnectedId(self, p, q):
        return self.__root(p) == self.__root(q)
    
    # @param row : int value of row
    # @param col : int value of col
    # @return id index of row, col
    def __gridToId(self, row, col):
        if row == 0 and col == 0:
            return 0
        elif row == self.n+1 and col == 0:
            return self.n * self.n + 1
        return 10 * (row-1) + col + 1
    
    # @param row : int value of grid row
    # @param col : int value of grid col
    def open(self, row, col):
        if row < self.first_row or row >= self.last_row or col < 0 or col >= self.n:
            raise ValueError('row < self.first_row or row >= self.last_row or col < 0 or col >= self.n')
        
        if self.grid[row][col] == 1:
            return
            
        self.grid[row][col] = 1
        
        dr = [ 0, 0, -1, 1]
        dc = [-1, 1,  0, 0]
        
        for rel_row, rel_col in zip(dr,dc):
            next_row = row + rel_row
            next_col = col + rel_col
            
            if next_row > 0 and next_row < self.last_row and next_col >= 0 and next_col < self.n:
                
                if self.grid[next_row][next_col] == 1:
                    p = self.__gridToId(row,col)
                    q = self.__gridToId(next_row,next_col)
                    self.__union(p,q)
            
        self.openSiteCount += 1
        
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
        p = self.__gridToId(row,col)
        
        # is grid[row][col] connected to virtual top site
        return self.__isConnectedId(p, self.virtual_top_site_id)
    
    # @param row : int value of grid row
    # @param col : int value of grid col
    # @param row : int value of grid row
    # @param col : int value of grid col
    # @return True if the two grid location are connected
    def isConnected(self, row, col, row2, col2):
        p = self.__gridToId(row, col)
        q = self.__gridToId(row2, col2)
        return self.__isConnectedId(p, q)
    
    # @return True if there is a connection from virtual top site to virtual bottom site
    def percolates(self):
        return self.__isConnectedId(self.virtual_top_site_id, self.virtual_bottom_site_id)

    # @return number of components
    def numberOfComponents(self):
        return self.componentsCount

    # @return the number of open sites
    def numberOfOpenSites(self):
        return self.openSiteCount
    
