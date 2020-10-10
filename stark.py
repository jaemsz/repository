'''
https://ctflearn.com/challenge/986
Programming challenge

After the Snap, Tony Stark and Nebula, were the only survivors on Titan. Lost in deep space for more than 20 days. 
As essentials are running out, Tony records his last message into the mask. But as fate happens, Captain Marvel recues 
Tony and Nebula. Later on, some weird data was found in the logs of Jarvis. The data was compressed. After looking at 
the data closely I found out that compression was lossless and was based on frequency of characters. Also, node data is 
pickled. When I decoded the data and read it, I was emotional. I can't exactly explain what I was feeling, but you will 
know what I felt, when you decode the data. 

info.txt:
https://ctflearn.com/challenge/download/986

Observations of info.txt:
1.  Contains an encoded binary string
    The encoded data was compressed using a lossless compression algorithm.  It looks like huffman codes.
    
2.  Contains a link to pickled data
    https://mega.nz/file/t5gSQa5I#cgLPXZCm_Kch3NLg9SZFsWX1ZssqBKWK4qdcTfRAfV4
    Upon opening the pickle file using python pickle module, I recieved an error:
        AttributeError: Can't get attribute 'Node' on <module '__main__' (built-in)>
    This means that when pickle saved the data to file, it did it from a class called Node.
    Once I was able to load the pickle data successfully, I ran a dir() on the returned data.
    dir() showed that there were attributes like data, left, right, which gave me the hint that the data contained a tree
    
Steps:
1.  Read pickle data
2.  Traverse the data using a standard traversal algorithm to get the huffman codes for each leaf node
3.  Substitute the huffman codes with the binary strings in the encoded data
4.  Base64 decode the result of huffman decompression
5.  Submit the flag
'''

import pickle
import base64

# create Node class, which will be used to 
class Node:
    def __init__(self):
        self.root = None
        
    def load_document(self):
        with open("node_data.txt", "rb") as f:
            self.root = pickle.load(f)
            
    def get_huffman_codes(self, root, path, res):
        if not root.left and not root.right:
            res[root.data] = path
        else:
            self.get_huffman_codes(root.left, path + [0], res)
            self.get_huffman_codes(root.right, path + [1], res)

node = Node()
node.load_document()

path = []
res = {}
node.get_huffman_codes(node.root, path, res)

encoded_data = '110110101000111001001100011010000100101011110101100110100011001110100100011001110000100011101000001001010111011010111110001101101001000001011010110011011001110010111010011010110011001010111011011011010000001110100100001011111101010011001000011000001111110100001011111000100001101011101011110010000101111001111101001010010001001110100100000101110101001111101100011101110001111101111010101111101000010011000111110010110111111000010011111111001111111011011010000100111100111010111011100011011111100010100011110101010011111110011110100110101100010101111011111110110100010101000110110111001000011011111101110101001111110111001001100011101111011100100101010010001100001110101000011000010001110100001001011110101011101011111110000010011000000'
decoded_data = ''

while len(encoded_data) > 0:
    for k,v in res.items():
        path_str = ''.join([str(v2) for v2 in v])
        if encoded_data.startswith(path_str):
            encoded_data = encoded_data[len(path_str):]
            decoded_data += str(k)
            
print(decoded_data)
# VG9ueV9TdGFyazpfSV9CdWlsZF9OZWF0X1N0dWZmLF9Hb3RfQV9HcmVhdF9HaXJsLF9PY2Nhc2lvbmFsbHlfU2F2ZV9UaGVfV29ybGQuX1NvX2ZsYWd7V2h5X0NhbuKAmXRfSV9TbGVlcD99

base64_bytes = decoded_data.encode('utf-8')
message_bytes = base64.b64decode(base64_bytes)
message = message_bytes.decode('utf-8')
print(message)
# Tony_Stark:_I_Build_Neat_Stuff,_Got_A_Great_Girl,_Occasionally_Save_The_World._So_flag{Why_Can’t_I_Sleep?}