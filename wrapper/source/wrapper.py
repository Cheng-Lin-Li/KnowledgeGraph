'''
Created on Sep 17, 2017

@author: Clark
'''
import os, sys, time, json, re
from bs4 import BeautifulSoup


def check_create_path(path):
    '''
    Create path for output
    '''
    if not os.path.isdir(path):
        os.makedirs (path) 
        
def get_content(inputfile):
    '''
    Get file name, load the JSON LINES data
    '''
    data_list = []
    with open(inputfile) as f:
        for line in f:
            data_list.append(json.loads(line))

    return data_list
        


def get_detail (html_doc):
    '''
    Extract article category, subject, content, publish date, total views and author.
    '''
    soup = BeautifulSoup(html_doc, 'html.parser')
    print(soup.h1.text)    
    if 'I Asked Jeff Bezos The Tough Questions  — No Profits, The Book Controversies' in soup.h1.text:
        print ('Stop') 

    # Get article category
    if soup.find('h2', class_ ='vert-name') is not None:
        category = ' '.join(soup.find('h2', class_ ='vert-name').text.split())
#     elif soup.find('h2', class_ ='vert-name ellipsis') is not None:
#         category = ' '.join(soup.find('h2', class_ ='vert-name ellipsis').text.split())
    else:
        category = None 
          
    # Get subject of the article
    if soup.h1 is not None:
        subject = soup.h1.text
    else:
        subject = None
    
    # Get content
    if soup.find('div', class_=re.compile('KonaBody post-content*')) is not None:
        content = ' '.join(soup.find('div', class_=re.compile('KonaBody post-content*')).text.split())
    elif soup.find('div', class_='intro-content') is not None:
        content = ' '.join(soup.find('div', class_='intro-content').text.split())
    else:
        content = None
    
    # Get publish date
    publishdate = soup.find('span', class_='svg sprites date-icon').next_sibling.next_sibling.text
    
    # Get page views
    if soup.find('span', title='Engagement') is not None:
        views = int(soup.find('span', title='Engagement').text.replace(',',''))
    else:
        views = None
    
#     # Get author from meta tag.
#     if soup.find('meta', property="author") is not None:
#         author = (soup.find('meta', property="author")['content'])       
    # Get author(s) name.
    if soup.find('li', class_='ks-author-byline') is not None:
        author = soup.find('li', class_='ks-author-byline').text.replace('and',',')
    elif soup.find('li', class_='single-author') is not None:
        author = soup.find('li', class_='single-author').text
    else:
        author = None
            
    if ',' in author:
        author = author.split(',')
    elif ' and ' in author:
        author = author.split(' and ')
    else:
        author = [author] 

    
    data = {'category':category, 'subject': subject, 'content': content, 
            'publish_date': publishdate, 'views': views, 'author': author}
    
   
    return data
def set_output(outfile_name, data_list):
    '''
    Generate JSON file format output
    JSON file specification:
        {
            "url": {
                "category": " Category Text ",
                "subject": "Subject Text",
                "content": "Article content",
                "publish_date": "Article publish date",
                "views": How many views on this article
                "author": ["author1", "author 2"...]
            },
        ...
        }

    '''
    i = 0
    output_obj = {}
    for json_data in data_list:      
        raw_html = json_data['raw_content'] #html page content

        data = get_detail(raw_html)
        output_obj[str(json_data['url'])] = data
        i += 1
        
    with open(outfile_name, 'w') as outfile:
        json.dump(output_obj, outfile, indent=4)
   

def main(input_file, output_path):  
    start = time.time()

    data_list = get_content(input_file)
    
    if output_path is not None:
        # Generate JSON output
        check_create_path(output_path)
        outfile_name = output_path + '/wrapper.json'    
        set_output(outfile_name, data_list)
        print('JSON file output has been generated.')
    else:
        print('Invalid output path.')

    end = time.time()

    print('runtime:', end - start)
    
    
if __name__ == '__main__':
    
    # Get input and output parameters
    if len(sys.argv) < 3:
        print('Usage: python ' + sys.argv[0] + ' <JSON Lines input file name> </output/path>')
        print('       The program requires Python 3.6 to execute.')   
        print('       - JSON Lines input file path = input file path of JSON Lines file')         
        print('       - output_path = Output file path of JSON file')    
        print('        Output JSON format:')       
        print('        {') 
        print('            "url": {') 
        print('                          "category": " Category Text ",') 
        print('                          "subject": "Subject Text",') 
        print('                          "content": "Article content",') 
        print('                          "publish_date": "Article publish date",')
        print('                          "views": How many views on this article,')
        print('                          "author": ["author1", "author 2"...]')
        print('            },')
        print('        ...')
        print('        }') 
                                                 
        exit ()    

    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_path = sys.argv[2]

        main(input_file, output_path)
    else:
        pass
            
