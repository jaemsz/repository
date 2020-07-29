# Dijkstra 2 stack algorithm
#
class Dijkstra:
    def evaluate(self, expr):
        val_stack = []
        op_stack = []
        
        N = len(expr)
        i = 0
        
        while i < N:            
            if expr[i] >= '0' and expr[i] <= '9':
                digits = ''
                while i < N and expr[i] >= '0' and expr[i] <= '9':
                    digits += expr[i]
                    i += 1
                    
                val_stack.append(float(digits))
                i -= 1
                
            elif expr[i] in ['+','-','*','/']:
                op_stack.append(expr[i])
                
            elif expr[i] == ')':
                v2 = val_stack.pop()
                v1 = val_stack.pop()
                op = op_stack.pop()
                
                if op == '+':   val_stack.append(v1 + v2)
                elif op == '-': val_stack.append(v1 - v2)
                elif op == '*': val_stack.append(v1 * v2)
                elif op == '/': val_stack.append(v1 / v2)
                    
            i = i + 1
            
        while op_stack:
            v2 = val_stack.pop()
            v1 = val_stack.pop()
            op = op_stack.pop()

            if op == '+':   val_stack.append(v1 + v2)
            elif op == '-': val_stack.append(v1 - v2)
            elif op == '*': val_stack.append(v1 * v2)
            elif op == '/': val_stack.append(v1 / v2)
            
        return val_stack.pop()
    
