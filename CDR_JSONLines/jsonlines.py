'''
Created on Sep 10, 2017

@author: Clark
'''
import matplotlib.pyplot as plt
import os, sys, time, json 
from urllib import parse
from hashlib import blake2b


def check_create_path(path):
    '''
    Create path for output
    '''
    if not os.path.isdir(path):
        os.makedirs (path) 
        
def get_information(directory):
    '''
    Get file name, create time, and file size information
    '''
    file_list = []
    for i in os.listdir(directory):
        file = os.stat(os.path.join(directory,i))
        file_list.append([i,time.ctime(file.st_ctime), file.st_size]) #[file, created time, file size]
    return file_list
        
def plot_histogram(file_sizes):
    '''
    Based on input size of files to plot the size vs number of files histogram 
    '''
    plt.hist(file_sizes, bins=500, histtype='stepfilled', color='b', label='html file size')
    plt.title("HTML file size/File number Histogram")
    plt.xlabel("HTML File size: KBytes")
    plt.ylabel("HTML File Numbers")
    plt.legend()
    plt.show()

def get_input (input_path, input_file):
    '''
    get input file by utf8 encoding. Read the file content then return it.
    '''
    with open(input_path+'/'+input_file, 'r', encoding='utf8') as f:
        data = f.read()
        f.close()    
    return data
def set_output(outfile_name, input_path, input_files, number_of_files):
    '''
    Generate JSON Lines format output
    JSON Lines specification:
        doc_id = unique number
        url = file URL
        raw_content = file content
        timestamp_crawl: When the file was been collected.
    '''
    files_size = []
    i = 0
    with open(outfile_name, 'w') as outfile:
        for file in input_files:
            if number_of_files > i or number_of_files == -1:        
                file_name = file[0] #file name is URL
                date_time = file[1]
                file_size = file[2]/1000 #KB
                data = get_input(input_path, file_name)
                json.dump({'url':parse.unquote(file_name), 'timestamp_crawl':date_time, 'raw_content':data, 'doc_id':blake2b(file_name.encode('utf-8'), digest_size=32).hexdigest()}, outfile)
                outfile.write('\n')
                i += 1   
                files_size.append(file_size)
            else:
                break
    outfile.close()
    return files_size    

def main(plot_picture, input_path=None, output_path=None, number_of_files = -1):
    files_size = []
    
    start = time.time()
        
    input_files = get_information(input_path)
    if output_path is not None:
        # Generate JSON Lines
        check_create_path(output_path)
        outfile_name = output_path + '/CDR.jl'    
        files_size = set_output(outfile_name, input_path, input_files, number_of_files)
    else :
        # Only plot the HTML file size distribute
        for file in input_files:
            file_size = file[2]/1000 #KB            
            files_size.append(file_size)

    end = time.time()
    print('CDR file has been generated.')
    print('runtime:', end - start)
    
    if plot_picture == True:
        plot_histogram(files_size)
    else:
        pass
    
if __name__ == '__main__':
    
    # Get input and output parameters
    if len(sys.argv) < 3:
        print('Usage: python ' + sys.argv[0] + ' <d> <html files input path> [output_path] [number of files]')
        print('       The program requires Python 3.6 to execute.')
        print('         d : Only draw the html file size distribution.')     
        print('         html files input path = input file path of html files')         
        print('         output_path = Optional, output file path of JSON Lines format')
        print('         number of files : Optional, number of html files you want to package into JSON Lines. Default value is all files.')                                             
        exit ()    

    if len(sys.argv) == 4:
        if sys.argv[1] == 'd':
            plot_picture = True
        else:
            plot_picture = False
            
        html_files = sys.argv[2]
        output_path = sys.argv[3]

        main(plot_picture, html_files, output_path)
    elif len(sys.argv) == 5:
        if sys.argv[1] == 'd':
            plot_picture = True
        else:
            plot_picture = False
            
        html_files = sys.argv[2]
        output_path = sys.argv[3]
        number_of_files = int(sys.argv[4])

        main(plot_picture, html_files, output_path, number_of_files)        
    elif len(sys.argv) == 3 and sys.argv[1] == 'd' :
        if sys.argv[1] == 'd':
            plot_picture = True
        else:
            plot_picture = False
            
        html_files = sys.argv[2]      
        main(plot_picture, html_files)
            
