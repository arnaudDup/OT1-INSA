# ------------------------------------------------------------------
# Import

import os 
import math
import operator
import collections
from bitarray import bitarray
import pickle

from util_posting import *
from fagin import top_k_thresh
# ------------------------------------------------------------------
# Constants 

ENCODE_PL_PICKLE_FILE = "../data/encode_pl_pickle_file"

# ------------------------------------------------------------------


class PostingListEncoder(object):
    """    
        Args :
        list_fst_lst_doc is a list of (first_word_of_the_block, last_word_of_the_block,file_number_of_the_block ) 
        dict_word_bgnPL_endPL is a dictionary assotiating word (string) to (first_bit_PL, last_bit_PL+1) (int,int)
    """
    def __init__(self, list_fst_lst_doc=[], dict_word_bgnPL_endPL={}, pl_file="../data/binPL/PL"):
        """

        :param list_fst_lst_doc:
        :param dict_word_bgnPL_endPL:
        :param pl_file:
        """
        self.list_fst_lst_doc=list_fst_lst_doc
        self.dict_word_bgnPL_endPL=dict_word_bgnPL_endPL
        self.pl_file=pl_file

    number_of_PL = 0

    
    def encode7bit(cls, value):
        """
        This function encode the integer <value> on the minimum octet necesary
        :param value: the int that will be encoded
        :return: bit array in forme of string that represent the value
        """
        temp =  value
        res = ''
        count = 0
        while temp > 0:
            if temp % 2 == 1:
                res = '1' + res
            else:
                res = '0'+ res
            temp //= 2
            count += 1
            if count % 8 == 7 and temp>0 :
                res = '0' + res
                count += 1
            
        while count % 8 != 7:
            res = '0' + res
            count += 1
        res = '1' + res
        return res
    encode7bit = classmethod(encode7bit)


    def decode7bit_one_oct(cls,my_str):
        """
        decode one array of 7 bit
        :param my_str: the 7 bits represented in a string
        :return: the intger represented by the string
        """
        temp = my_str
        order = 1
        res = 0
        while temp != []:
            bit = temp.pop(len(temp)-1)
            if bit == '1' :
                res += order
            order *= 2
        return res
    decode7bit_one_oct = classmethod(decode7bit_one_oct)

    def decode7bit_one_int(cls,my_str):
        """
        decode an array of bit of several octet that represent a unique integer
        :param my_str: the bits represented in a string
        :return: the intger represented by the bit array
        """
        temp = list(my_str)
        order = 1
        res = 0
        while temp != []:
            param = temp[len(temp)-8:]
            param.pop(0)
            res += order * PostingListEncoder.decode7bit_one_oct(param)
            temp = temp[:len(temp)-8]
            order*=128
        return res
    decode7bit_one_int = classmethod(decode7bit_one_int)

    def decode7bit_list_int(cls,mystr):
        """
        decode an array of bit of several octet that represent serveral integer
        :param mystr: the bits represented in a string
        :return: the intger represented by the bit array
        """
        temp = mystr
        res = []
        next_str = "" 
        while temp != "":
            next_str += temp[:8]
            temp = temp[8:]
            if temp != "":
                while temp[0] != '1':
                    next_str += temp[:8]
                    temp = temp[8:]
                    if temp == "":
                        break
            res.append(PostingListEncoder.decode7bit_one_int(next_str))
            next_str = ""
        return res
    decode7bit_list_int = classmethod(decode7bit_list_int)


    def encode7bit_list_int(cls,l):
        """
        encode a list of int
        :param l: the list of int that we want to encode
        :return: string that represent the list of int encoded
        """
        res = ""
        for i in l:
            res += PostingListEncoder.encode7bit(i)
        return res
    encode7bit_list_int = classmethod(encode7bit_list_int)

    def bitarray_to_string(cls,ba):
        """
        represent the bit array
        :param ba: bit array
        :return: the string that contain each bit
        """
        return ba.__repr__()[10:len(ba.__repr__())-2]
    bitarray_to_string = classmethod(bitarray_to_string)

    def encode_posting_list(cls,dict_doc_score):
        """
        encode a posting list
        :param dict_doc_score: dict that have a doc id as key and a score as value
        :return: the bitarray object that represent the posting list
        """
        list_of_int = []
        for key, val in dict_doc_score.items():
            list_of_int.append(int(key))
            prev = int(val)                      
            list_of_int.append(int(val))
            del dict_doc_score[key]
            break

        for key, val in dict_doc_score.items():
            list_of_int.append(int(key))
            diff = int(val)-prev
            list_of_int.append(int(diff))
            prev = int(val)

        return bitarray(PostingListEncoder.encode7bit_list_int(list_of_int))
    encode_posting_list = classmethod(encode_posting_list)

    def decode_posting_list(cls,bit_array):
        """
        decode a bit array that represent a posting list
        :param bit_array: the bitarray object that represent the posting list
        :return: a list in the form of [doc_id, score, doc_id, score, ...]
        """
        list_of_doc_and_diff = PostingListEncoder.decode7bit_list_int(PostingListEncoder.bitarray_to_string(bit_array))
        prev = 0
        for i in range(1,len(list_of_doc_and_diff),2):
            list_of_doc_and_diff[i] = list_of_doc_and_diff[i] + prev
            prev = list_of_doc_and_diff[i]
        return list_of_doc_and_diff
    decode_posting_list = classmethod(decode_posting_list)

    def add_block_of_PL(self, list_word_PL):
        """
        Encode a set of posting list ordrer by word and each posting list is ordred by score ascending
        :param list_word_PL: list of (word, {doc_id: score, ...} )
        :return: Nothing
        """
        # add of block

        PostingListEncoder.number_of_PL +=1 
        number_of_PL = PostingListEncoder.number_of_PL
        self.list_fst_lst_doc.append( (list_word_PL[0][0], list_word_PL[len(list_word_PL)-1][0], number_of_PL))

        # make PL 
        bit_block = bitarray()
        begin_PL = 0
        end_PL = 0
        for tp in list_word_PL:
            word = tp[0]
            word_bitarray = PostingListEncoder.encode_posting_list(tp[1])
            end_PL += len(word_bitarray)
            bit_block += word_bitarray
            self.dict_word_bgnPL_endPL[word] = (begin_PL,end_PL)
            begin_PL = end_PL
        with open(self.pl_file + str(number_of_PL), 'wb') as file:
            my_pickler = pickle.Pickler(file)
            my_pickler.dump(bit_block)


    def get_posting_list(self, word):
        """
        Get the postiong list of a specifique word
        :param word: the word which is associat to the posting list that we want
        :return: posting list in the form of (word, {doc_id:score})
        """
        if word in self.dict_word_bgnPL_endPL.keys():  
            n_PL = 0 
            for t in self.list_fst_lst_doc:
                if t[0] <= word and t[1] >= word:
                    n_PL = t[2]
                    break
            bit_block = bitarray()
            with open(self.pl_file + str(n_PL), 'rb') as file:
                my_unpickler = pickle.Unpickler(file)
                bit_block = my_unpickler.load()
            start = self.dict_word_bgnPL_endPL[word][0]
            end = self.dict_word_bgnPL_endPL[word][1]
            list_doc_score = PostingListEncoder.decode_posting_list(bit_block[start:end])
            dict_doc_score = {}
            for i in range(0, len(list_doc_score)-1, 2):
                dict_doc_score[list_doc_score[i]] = list_doc_score[i+1]
            return (word, dict_doc_score)


    def creat_posting_list_obj(self,posting_list):
        """
        Create a posting list object
        :param posting_list: (word, {doc_id: score, ...})
        :return: Posting list obj coresponding
        """
        qt = posting_list[0]
        ordered_list = []
        access_dict = {}
        
        for key, val  in posting_list[1].items():
            doc_id = key
            score = val
            ordered_list.append((float(score),int(doc_id)))
            access_dict[int(doc_id)] = float(score)
            ######## here
        ordered_list.reverse()
        ########
        return PostingList(qt,ordered_list,access_dict)

    def creat_posting_list_obj_list(self,query):
        """
        Create and return all the posting list corespnding to a query
        :param query: string mcontaining the semified word of the query separat by blank space
        :return: list of PostinList object
        """
        posting_list_obj_list = []
        word_list = query.split()
        for word in word_list:
            posting_list_obj = self.creat_posting_list_obj(self.get_posting_list(word))
            posting_list_obj_list.append(posting_list_obj)
        return posting_list_obj_list
            
            
            
        
def current_word_PL(current_word, file_reader_last_read_list, doc_dict, nb_doc):
    """

    :param current_word:
    :param file_reader_last_read_list:
    :param doc_dict:
    :param nb_doc:
    :return:
    """
    word_posting_list = {} # { key = doc , value = score }
    for idx, file_reader_last_read in enumerate(file_reader_last_read_list):
        if file_reader_last_read["last_read"]["word"] == current_word:
            docs = file_reader_last_read["last_read"]["doc_score_list"]
            add_doc_in_posting_list(word_posting_list=word_posting_list, docs=docs)
            file_reader_last_read_list[idx]=read_line_and_update(file_reader_and_last_read=file_reader_last_read)
    for key, value in word_posting_list.items():
        tf = float(value) / doc_dict[int(key)]
        idf = math.log((float(nb_doc)/len(word_posting_list)),10)
        score  = (tf*idf)
        word_posting_list[key]= int(score*1000000000) 
    word_posting_list = sort_and_cast_doc_in_posting_list(word_posting_list=word_posting_list)
    return word_posting_list
    


def createPostingListEncoded(block_size=1000):
    """
    Create the posting list encoded and reteur the postingListEncoder object that can access to them
    :param block_size: number of word referenced n each block
    :return:  postingListEncoder object that can access to the encoded posting list
    """
    try :
        ##### peut etre à mettre dans une fonction
        file_reader_last_read_list = initialize_file_readers()
        for idx, file_reader_and_last_read in enumerate(file_reader_last_read_list):
            file_reader_last_read_list[idx]=read_line_and_update(file_reader_and_last_read=file_reader_and_last_read)
        current_word = min_top_word(file_reader_last_read_list=file_reader_last_read_list)
        ######

        doc_dict = get_doc_dict("../data/util/docList")
        nb_doc = len(doc_dict)

        ### autre function
        myPostingListEncoder = PostingListEncoder()
        counter = 0 
        block = []
        while current_word != "|||":    
            current_PL = current_word_PL(current_word=current_word, file_reader_last_read_list=file_reader_last_read_list,\
             doc_dict=doc_dict, nb_doc=nb_doc ) 
            temp = {}
            for key, value in current_PL.items():
                temp[int(key)]=int(value)
            block.append((current_word, temp))
            current_word = min_top_word(file_reader_last_read_list=file_reader_last_read_list)
            if counter%block_size == 0:
                myPostingListEncoder.add_block_of_PL(block)
                block = []
                # print(counter/block_size)
            counter +=1
        ####
        close_file_readers(file_reader_last_read_list=file_reader_last_read_list)
        return myPostingListEncoder
    
    except Exception as ex:
        
        close_file_readers(file_reader_last_read_list=file_reader_last_read_list)
        raise ex
        
def saveEncoderInPickle(obj, filename):
    """
    Save the postingListEncoder into a pickle file
    :param obj: the postingListEncoder
    :param filename: the pickle file name
    :return: Nothing
    """
    with open(filename, 'wb') as file:
        my_pickler = pickle.Pickler(file)
        my_pickler.dump(obj)
    
def unPickleEncoder(filename):
    """
    Load a postingListEncoder object
    :param filename: The name of the file which contain the Encoder
    :return: the encoder object
    """
    with open(filename, 'rb') as file:
        my_unpickler = pickle.Unpickler(file)
        return my_unpickler.load()

def initialize_encoded_PL_obj():
    """
    Create the encoded posting list and file the Encoder object into a pickle
    :return: Nothing
    """
    saveEncoderInPickle(createPostingListEncoded(), ENCODE_PL_PICKLE_FILE)
    
def get_encoded_PL_obj():
    """
    Load the encoder object from a predefined pickle file name
    :return: The encoder object
    """
    return unPickleEncoder(ENCODE_PL_PICKLE_FILE)


def manage_request_with_encoded_pl(my_r_string, k=5):
    """
    Take a string request and return the top file coresponding to this request by using the fagin algorithm
    :param my_r_string: the request string
    :param k: the number of doc id in the top
    :return: The list of the top doc id coresponding to the request
    """
    encoded_pl = get_encoded_PL_obj()
    stem_r_str = handleFormatText(my_r_string)
    posting_lists = encoded_pl.creat_posting_list_obj_list(stem_r_str)
    result = top_k_thresh(posting_lists, k, epsilon=0.0)
    return result



