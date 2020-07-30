# dequeue implemented using doubly linked list
#
class DequeueDLList:
    # iterator for the dequeue
    class DequeueDLListIterator:
        def __init__(self, dequeueDLList):
            self.dequeueDLList = dequeueDLList
            self.curr = self.dequeueDLList.head

        def __next__(self):
            if self.curr:
                item = self.curr.item
                self.curr = self.curr.next
                return item

            raise StopIteration
            
    # definition of a node for the doubly linked list
    class Node:
        # initialize val an next
        def __init__(self, item):
            self.item = item
            self.next = None
            self.prev = None
        
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0
    
    # @return : True if the dequeue is empty, otherwise False
    def isEmpty(self):
        if self.count != 0:
            return False
        return True
    
    # @return : length of the dequeue
    def __len__(self):
        return self.count
    
    # @param item : push the item to the front of the dequeue
    def pushFront(self, item):
        newNode = self.Node(item)
        
        if not self.head:
            newNode.next = None
            self.head = newNode
            self.tail = newNode
            
        else:            
            self.head.prev = newNode
            temp = self.head
            self.head = newNode
            newNode.next = temp
            
        self.count += 1
    
    # @param item : push the item to the back of the dequeue
    def push(self, item):
        newNode = self.Node(item)
        
        if not self.head:
            newNode.next = None
            self.head = newNode
            self.tail = newNode
            
        else:
            newNode.next = None
            newNode.prev = self.tail
            self.tail.next = newNode
            self.tail = newNode
            
        self.count += 1
    
    # @return : pop an item off the front of the dequeue
    def popFront(self):
        item = None
        
        if self.head and self.head == self.tail:
            # only 1 item in the list
            item = self.head.item
            self.head = None
            self.tail = None
                        
        elif self.head:
            item = self.head.item
            self.head = self.head.next
            self.head.prev = None
            
        if item:
            self.count -= 1
            
        return item
    
    # @return : pop an item off the back of the dequeue
    def pop(self):
        item = None
        
        if self.head and self.head == self.tail:
            # only 1 item in the list
            item = self.head.item
            self.head = None
            self.tail = None
            
        elif self.tail:
            item = self.tail.item
            self.tail = self.tail.prev
            self.tail.next = None
            
        if item:
            self.count -= 1
        
        return item
    
    # @return : return an iterator for the dequeue object
    def __iter__(self):
        return self.DequeueDLListIterator(self)
        
