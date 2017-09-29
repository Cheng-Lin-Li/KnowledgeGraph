#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Sep 25, 2017

@author: Clark
'''
import os, sys, time, json, re, string
from bs4 import BeautifulSoup
from wrapper.wrapper import get_detail

def check_create_path(path):
    '''
    Create path for output
    '''
    if not os.path.isdir(path):
        os.makedirs (path) 
        
def get_input (input_path, input_file):
    '''
    get input file by utf8 encoding. Read the file content then return it.
    '''
    with open(input_path+'/'+input_file, 'r', encoding='utf8') as f:
        data = f.read()
        f.close()    
    return data
        
def get_information(directory):
    '''
    Get file name, create time, and file size information
    '''
    file_list = []
    for i in os.listdir(directory):
        file = os.stat(os.path.join(directory,i))
        file_list.append([i,time.ctime(file.st_ctime), file.st_size]) #[file name, created time, file size]
    return file_list

def get_detail (html_doc):
    '''
    Extract textbook information from syllabus.
    '''
    
    soup = BeautifulSoup(html_doc, 'html.parser') 
    texts=soup.get_text().replace('\n', ' ')
#     print('text=%s'%(texts))
    pattern = re.compile(r' (texts|textbooks|textbook|text:|texts and readings|texts and materials'
            + '|texts and reading:|text that you should purchase|text is|books for purchase:|'
            +'books|text).{720}', re.S|re.I) #Get 702 characters
    data = re.search(pattern,texts)
    if data is not None:
        textbooks = data.group(0).strip()
    else:
        textbooks = None
   
    return textbooks 

def get_input (input_file):
    '''
    get input file by utf8 encoding. Read the file content then return it.
    '''
    with open(input_file, 'r', encoding='utf8') as f:
        data = f.read()
        f.close()    
    return data

def ispunchuation(word):
    return True if word in string.punctuation else False

def get_token (sentence, delimiter, label):
    '''
    Split sentence to tokens per word
    '''
    tokens = ''
    
    for i in range(0, len(sentence)):
        c = sentence[i]
        splitter = delimiter + irrelevant_label + '\n'
        if ispunchuation(c) or c == ')' or c == '(':
            tokens += splitter + c + splitter
        elif c == ' ':
            if tokens[-len(splitter)] == splitter:
                pass # skip continuous space
            else:
                tokens += splitter
        else:
            tokens += c   
    return tokens

def set_output(outfile_name, input_path, input_files, delimiter, irrelevant_label):
    '''
    Get html file and extract textbook information
    '''
    with open(outfile_name, 'wb') as outfile:
        for file in input_files:
#             print (input_path+ '/' + file[0])
            data = get_input(input_path+ '/' + file[0]) #input path + file name
            textbook = get_detail(data)
            if delimiter is None: #output sentences per line
                outfile.write(textbook.encode('utf-8', 'ignore'))

            else: # Output token per line with delimiter and default irrelevant tag/label
                tokens = get_token(textbook, delimiter, irrelevant_label)
                outfile.write(tokens.encode('utf-8', 'ignore'))
            
            outfile.write('\n\n'.encode('utf-8'))
    outfile.close()   
    if delimiter is None:
        print('Data extraction completed.')
    else:
        print('Data extraction completed and tokenized.')   

def main(input_path, output_path, delimiter, irrelevant_label):
    start = time.time()

    input_files = get_information(input_path)
    
    # Generate JSON Lines
    check_create_path(output_path)
    outfile_name = output_path + '/extract.csv'    
    set_output(outfile_name, input_path, input_files, delimiter, irrelevant_label)

    end = time.time()

    print('runtime:', end - start)
    
    
if __name__ == '__main__':
    
    # Get input and output parameters
    if len(sys.argv) < 3:
        print('Usage: python ' + sys.argv[0] + ' <input html files path> </output/path> [delimiter for token] [irrelevant label]')
        print('       The program requires Python 3.6 to execute.')   
        print('       - input_path = input file path of html files')         
        print('       - output_path = Output file path of csv file')   
        print('       - delimiter for token = Optional, if provide, Output sentences will convert to token + delimiter')  
        print('       - irrelevant label = Optional, if provide, the label/tag will be appended after the delimiter, default = \'N\'')                   
        print('        Output format:')
        print('            One line per sentence:')
        print('        Or, if delimiter=\'|\' and label=\'N\'')
        print('            One|N')                               
        print('            word|N') 
        print('            per|N') 
        print('            row|N')                 

                                                 
        exit ()    
        
    delimiter = None
    irrelevant_label = 'N'
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]

    elif len(sys.argv) == 4:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        delimiter = sys.argv[3]

    elif len(sys.argv) == 5:
        input_path = sys.argv[1]
        output_path = sys.argv[2]    
        delimiter = sys.argv[3]
        irrelevant_label = sys.argv[4]                            
    else:
        exit()
        
    main(input_path, output_path, delimiter, irrelevant_label)
            
