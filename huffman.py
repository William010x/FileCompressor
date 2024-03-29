"""
Code for compressing and decompressing using Huffman compression.
"""

from nodes import HuffmanNode, ReadNode


# ====================
# Helper functions for manipulating bytes


def get_bit(byte, bit_num):
    """ Return bit number bit_num from right in byte.

    @param int byte: a given byte
    @param int bit_num: a specific bit number within the byte
    @rtype: int

    >>> get_bit(0b00000101, 2)
    1
    >>> get_bit(0b00000101, 1)
    0
    """
    return (byte & (1 << bit_num)) >> bit_num


def byte_to_bits(byte):
    """ Return the representation of a byte as a string of bits.

    @param int byte: a given byte
    @rtype: str

    >>> byte_to_bits(14)
    '00001110'
    """
    return "".join([str(get_bit(byte, bit_num))
                    for bit_num in range(7, -1, -1)])


def bits_to_byte(bits):
    """ Return int represented by bits, padded on right.

    @param str bits: a string representation of some bits
    @rtype: int

    >>> bits_to_byte("00000101")
    5
    >>> bits_to_byte("101") == 0b10100000
    True
    """
    return sum([int(bits[pos]) << (7 - pos)
                for pos in range(len(bits))])


# ====================
# Functions for compression


def make_freq_dict(text):
    """ Return a dictionary that maps each byte in text to its frequency.

    @param bytes text: a bytes object
    @rtype: dict(int,int)

    >>> d = make_freq_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    freq = {}
    for byte in text:
        freq[byte] = freq.get(byte, 0) + 1
    return freq


def huffman_tree(freq_dict):
    """ Return the root HuffmanNode of a Huffman tree corresponding
    to frequency dictionary freq_dict.

    @param dict(int,int) freq_dict: a frequency dictionary
    @rtype: HuffmanNode

    >>> freq = {2: 6, 3: 4}
    >>> t = huffman_tree(freq)
    >>> result1 = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> result2 = HuffmanNode(None, HuffmanNode(2), HuffmanNode(3))
    >>> t == result1 or t == result2
    True
    """
    freq = list(freq_dict.items())
    
    if len(freq) == 1:
        return HuffmanNode(None, HuffmanNode(freq[0][0]), None)
    
    while len(freq) != 1:
        x = take_min(freq)
        y = take_min(freq)
        total = x[1] + y[1]
        
        if isinstance(x[0], HuffmanNode):
            left = x[0]
        else:
            left = HuffmanNode(x[0])
        if isinstance(y[0], HuffmanNode):
            right = y[0]
        else:
            right = HuffmanNode(y[0])
        
        root = HuffmanNode(None, left, right)
        freq.append((root, total))
    
    return root


def take_min(lst):
    """ Return the key, value tuple corresponding to the lowest value, and 
    removes that tuple from lst.

    @param list(tuple(int|HuffmanNode,int)) lst: tuples relating to frequencies
    @rtype: tuple(int|HuffmanNode,int)

    >>> d = [(1, 10), (2, 6), (3, 4), (HuffmanNode(4, None, None), 5)]
    >>> take_min(d)
    (3, 4)
    >>> d
    [(1, 10), (2, 6), (HuffmanNode(4, None, None), 5)]
    >>> take_min(d)
    (HuffmanNode(4, None, None), 5)
    >>> d
    [(1, 10), (2, 6)]
    """
    smallest_value = lst[0][1]
    smallest_key = lst[0][0]
    
    for key, value in lst:
        if value < smallest_value:
            smallest_key = key
            smallest_value = value
    lst.remove((smallest_key, smallest_value))

    return smallest_key, smallest_value


def get_codes(tree):
    """ Return a dict mapping symbols from Huffman tree to codes.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: dict(int,str)

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    """
    codes = {}
    
    if tree == None:
        return {}
    
    if tree.left.is_leaf():
        codes[tree.left.symbol] = "0"
    else:
        left = get_codes(tree.left)
        for key in left.keys():
            left[key] = "0" + left[key]
        codes.update(left)
        
    if tree.right.is_leaf():
        codes[tree.right.symbol] = "1"
    else:
        right = get_codes(tree.right)
        for key in right.keys():
            right[key] = "1" + right[key]
        codes.update(right)
        
    return codes


def number_nodes(tree):
    """ Number internal nodes in tree according to postorder traversal;
    start numbering at 0.

    @param HuffmanNode tree:  a Huffman tree rooted at node 'tree'
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(None, HuffmanNode(9), HuffmanNode(10))
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """
    numbering(tree, 0)


def numbering(tree, n):
    """ Number internal nodes in tree according to postorder traversal;
    start numbering at n.

    @param HuffmanNode tree:  a Huffman tree rooted at node 'tree'
    @rtype: int
    """
    if not tree.is_leaf():
        n = numbering(tree.left, n)
        n = numbering(tree.right, n)
        tree.number = n
        n += 1
    return n


def avg_length(tree, freq_dict):
    """ Return the number of bits per symbol required to compress text
    made of the symbols and frequencies in freq_dict, using the Huffman tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: float

    >>> freq = {3: 2, 2: 7, 9: 1}
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(9)
    >>> tree = HuffmanNode(None, left, right)
    >>> avg_length(tree, freq)
    1.9
    """
    #This, for some reason is incorrect even though it passes this doctest, it does not pass another doctest inside the improve_tree function
    total = 0
    avg = 0
    codes = get_codes(tree)
    d = {}
    #for key in freq:
        #total += freq_dict[key]
    for key in codes:
        total += freq_dict[key]
        avg += len(codes[key]) * freq_dict[key]
    avg = avg / total
    return avg

#total = 0
#avg = 0
#codes = get_codes(tree)
#prob = {}
#for key in freq_dict:
    #total += freq_dict[key]
#for key in codes:
    #prob[key] = freq_dict[key] / total
    #avg += len(codes[key]) * prob[key]
#return avg


def generate_compressed(text, codes):
    """ Return compressed form of text, using mapping in codes for each symbol.

    @param bytes text: a bytes object
    @param dict(int,str) codes: mapping from symbols to codes
    @rtype: bytes

    >>> d = {0: "0", 1: "10", 2: "11"}
    >>> text = bytes([1, 2, 1, 0])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111000']
    >>> text = bytes([1, 2, 1, 0, 2])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111001', '10000000']
    """
    y = []
    byte = ""
    
    for i in text:
        if len(byte) + len(codes[i]) > 8:
            byte = byte + codes[i]
            extra = byte[8:]
            y.append(bits_to_byte(byte[0:8]))
            byte = extra
        else:
            byte = byte + codes[i]
    y.append(bits_to_byte(byte))
    
    return bytes(y)


def tree_to_bytes(tree):
    """ Return a bytes representation of the Huffman tree rooted at tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes

    The representation should be based on the postorder traversal of tree
    internal nodes, starting from 0.
    Precondition: tree has its nodes numbered.

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2]
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(5)
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2, 1, 0, 0, 5]
    """
    lst = []
    if not tree.left.is_leaf():
        lst += tree_to_bytes(tree.left)
    if not tree.right.is_leaf():
        lst += tree_to_bytes(tree.right)
    
    if tree.left.is_leaf():
        lst.append(0)
        lst.append(tree.left.symbol)
    else:
        lst.append(1)
        lst.append(tree.left.number)
    if tree.right.is_leaf():
        lst.append(0)
        lst.append(tree.right.symbol)
    else:
        lst.append(1)
        lst.append(tree.right.number)
    return bytes(lst)


def num_nodes_to_bytes(tree):
    """ Return number of nodes required to represent tree (the root of a
    numbered Huffman tree).

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes
    """
    return bytes([tree.number + 1])


def size_to_bytes(size):
    """ Return the size as a bytes object.

    @param int size: a 32-bit integer to convert to bytes
    @rtype: bytes

    >>> list(size_to_bytes(300))
    [44, 1, 0, 0]
    """
    # little-endian representation of 32-bit (4-byte)
    # int size
    return size.to_bytes(4, "little")


def compress(in_file, out_file):
    """ Compress contents of in_file and store results in out_file.

    @param str in_file: input file to compress
    @param str out_file: output file to store compressed result
    @rtype: NoneType
    """
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = make_freq_dict(text)
    tree = huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    print("Bits per symbol:", avg_length(tree, freq))
    result = (num_nodes_to_bytes(tree) + tree_to_bytes(tree) +
              size_to_bytes(len(text)))
    result += generate_compressed(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)


# ====================
# Functions for decompression


def generate_tree_general(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes nothing about the order of the nodes in node_lst.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in 'node_lst'
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 1, 1, 0)]
    >>> generate_tree_general(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(10, None, None), \
HuffmanNode(12, None, None)), \
HuffmanNode(None, HuffmanNode(5, None, None), HuffmanNode(7, None, None)))
    """
    x = node_lst[root_index]
    if x.l_type:
        left = generate_tree_general(node_lst, x.l_data)
    else:
        left = HuffmanNode(x.l_data)
    if x.r_type:
        right = generate_tree_general(node_lst, x.r_data)
    else:
        right = HuffmanNode(x.r_data)
    return HuffmanNode(None, left, right)


def generate_tree_postorder(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes that node_lst represents a tree in postorder.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in 'node_lst'
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> generate_tree_postorder(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(5, None, None), \
HuffmanNode(7, None, None)), \
HuffmanNode(None, HuffmanNode(10, None, None), HuffmanNode(12, None, None)))
    """
    q = []
    for x in node_lst:
        if x.l_type == 1:
            left = q.pop(0)
        else:
            left = HuffmanNode(x.l_data)
        
        if x.r_type == 1:
            right = q.pop(0)
        else:
            right = HuffmanNode(x.r_data)
        
        root = HuffmanNode(None, left, right)
        q.append(root)
    
    return q[0]


def generate_uncompressed(tree, text, size):
    """ Use Huffman tree to decompress size bytes from text.

    @param HuffmanNode tree: a HuffmanNode tree rooted at 'tree'
    @param bytes text: text to decompress
    @param int size: number of bytes to decompress from text.
    @rtype: bytes
    
    
    """
    code = ""
    decode = []
    index = 0
    start = 0
    counter = 1
    
    freq = get_codes(tree)
    reverse = {}
    for key, value in freq.items():
        reverse[value] = key
        
    while len(decode) < size and index < len(text):
        short = False
        code = code + byte_to_bits(text[index])
        
        while not short and len(decode) < size:
            while not short and code[start:counter] not in reverse:
                counter += 1
                if counter > len(code):
                    short = True
            
            if not short:
                decode.append(reverse[code[start:counter]])
                start = counter
        
        index += 1    
        
    #while len(decode) < size and index < len(text):
        #short = False
        #code = code + byte_to_bits(text[index])
        
        #while not short and len(decode) < size:
            #counter = 1
            #while not short and code[:counter] not in reverse:
                #counter += 1
                #if counter > len(code):
                    #short = True
            
            #if not short:
                #decode.append(reverse[code[:counter]])
                #code = code[counter:]
        
        #index += 1
    
    #while len(decode) < size and index < len(text):
        #short = False
        #code = code + byte_to_bits(text[index])
        
        #while not short and len(decode) < size:
            #leaf = find_leaf(tree, code)
            #if leaf != False:
                #(d, counter) = leaf
                #code = code[counter:]
                #decode.append(d)
            #else:
                #short = True
        
        #index += 1
    
        
    #for byte in text:
        #code = code + byte_to_bits(byte)
    #nstart = 0
    #index = 1
    #while len(decode) < size:
        #while code[nstart:index] not in reverse:
            #index += 1
        #decode.append(reverse[code[nstart:index]])
        #nstart = index
        
    return bytes(decode)


def bytes_to_nodes(buf):
    """ Return a list of ReadNodes corresponding to the bytes in buf.

    @param bytes buf: a bytes object
    @rtype: list[ReadNode]

    >>> bytes_to_nodes(bytes([0, 1, 0, 2]))
    [ReadNode(0, 1, 0, 2)]
    """
    lst = []
    for i in range(0, len(buf), 4):
        l_type = buf[i]
        l_data = buf[i+1]
        r_type = buf[i+2]
        r_data = buf[i+3]
        lst.append(ReadNode(l_type, l_data, r_type, r_data))
    return lst


def bytes_to_size(buf):
    """ Return the size corresponding to the
    given 4-byte little-endian representation.

    @param bytes buf: a bytes object
    @rtype: int

    >>> bytes_to_size(bytes([44, 1, 0, 0]))
    300
    """
    return int.from_bytes(buf, "little")


def uncompress(in_file, out_file):
    """ Uncompress contents of in_file and store results in out_file.

    @param str in_file: input file to uncompress
    @param str out_file: output file that will hold the uncompressed results
    @rtype: NoneType
    """
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        # use generate_tree_general or generate_tree_postorder here
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_size(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(generate_uncompressed(tree, text, size))


# ====================
# Other functions

def improve_tree(tree, freq_dict):
    """ Improve the tree as much as possible, without changing its shape,
    by swapping nodes. The improvements are with respect to freq_dict.

    @param HuffmanNode tree: Huffman tree rooted at 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(99), HuffmanNode(100))
    >>> right = HuffmanNode(None, HuffmanNode(101), \
    HuffmanNode(None, HuffmanNode(97), HuffmanNode(98)))
    >>> tree = HuffmanNode(None, left, right)
    >>> freq = {97: 26, 98: 23, 99: 20, 100: 16, 101: 15}
    >>> improve_tree(tree, freq)
    >>> avg_length(tree, freq)
    2.31
    """
    # todo

if __name__ == "__main__":
    import doctest
    #doctest.testmod()

    import time

    mode = input("Press c to compress or u to uncompress: ")
    if mode == "c":
        fname = input("File to compress: ")
        start = time.time()
        compress(fname, fname + ".huf")
        print("compressed {} in {} seconds."
              .format(fname, time.time() - start))
    elif mode == "u":
        fname = input("File to uncompress: ")
        start = time.time()
        uncompress(fname, fname + ".orig")
        print("uncompressed {} in {} seconds."
              .format(fname, time.time() - start))
