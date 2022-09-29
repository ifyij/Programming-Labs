import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6



def get_link(url):
    """
    Given a url in the form of a string
    Returns the redirected http response object associated with the final destination
    and raises an error depending on the status, or simply returns the http response object
    if there is no redirect

    """
    
    try:
        r = http_response(url) #to make sure this call works
    except:
        raise HTTPRuntimeError #raises error otherwise

    status = r.status
    if status == 404:
        raise HTTPFileNotFoundError
    elif status == 500:
        raise HTTPRuntimeError
    elif status == 301 or status == 302 or status == 307:
        return get_link(r.getheader('location')) #keep getting redirected link
    else:
        return http_response(url) #return http response object associated with url
    
def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    
    r = get_link(url) #getting the object
    
    

    if url.endswith('.parts') or r.getheader('content-type') == 'text/parts-manifest': #checking to see if the url is a manifest
        cache = {} #cache rep is a dictionary; keys: url, values: bytestring file
        current = r.readline() #the current line in the manifest
        while current != b'': #making sure there are still lines in the manifest, going through every section in the manifest
            section = [] #a section of the manifest
            while current != b'--\n' and current != b'': #indicates moving on to the next section of the manifest
                section.append(current) #section is a list of each line in a section of the manifest
                current = r.readline() #getting the next line in the list
            downloaded = False #if a file from that section has been downloaded
            add_to_cache = False #if something should be added to the cache
           
            if b'(*)\n' in section: #if something can be cached
                for ele in section:
                    if ele.decode().strip() in cache: #getting things from the cache
                        yield cache[ele.decode().strip()] 
                        downloaded = True #already downloaded file from that manifest section
                        break
                if downloaded == False: #none of the urls were in the cache
                    for ele in section:
                        try: #some of the urls dont work
                            file_contents = b'' #getting the file contents of that specific url
                            for chunk in download_file(ele.decode().strip(), chunk_size): 
                                yield chunk
                                file_contents += chunk #building file from the url
                            downloaded = True
                            add_to_cache = True #add file contents to the cache
                        except:
                            continue
                if add_to_cache: 
                    for ele in section: #every url in the section is added to the cache with the file yielded
                        if ele != b'(*)\n' and ele.decode().strip() not in cache:
                            cache[ele.decode().strip()] = file_contents
           
            else: #not cacheable           
                for ele in section:
                    if downloaded: #so that the remaining urls are not checked
                        break
                    else:
                        try:
                           yield from download_file(ele.decode().strip(), chunk_size) #might not work
                           downloaded = True #stop downloading in this section of the manifest
                        except:
                            continue #try the next one in the section
                        
                    
            current = r.readline() #indicates new section        
            
    else:
        #yielding file in chunks
        file_chunk = r.read(chunk_size) 
        while file_chunk != b'': #b'' indicates the end of the file
            yield file_chunk
            file_chunk = r.read(chunk_size)    
        
    
        


def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    #boolean for currently looking in yielded chunk for the 
    #4-index long bytestring indicating size of the next file
    get_size = True 
    curr_size = b'' #current bytestring for the size
    curr_file = b'' #current bytestring for the file
    size = 0 #size of the file we're looking for
    index =0 #index that we're on for the bytestring
    next_ind = 0 #the next index
    ele = next(stream) #the first chunk of the file
    while True: #a way to alternate between getting the size bytestring and the file bytestring
        while get_size:
            next_ind = index + 4 - len(curr_size) #the next index if you're looking for a size
            if next_ind <= len(ele): #the rest of the size or the whole size is in the chunk
                curr_size += ele[index:next_ind] #getting the size bytestring
                size = int.from_bytes(curr_size, 'big') #getting the size
                #resetting variables
                get_size = False
                index = next_ind 
                curr_size = b''
            else: #the rest of the size is in the next chunk
                curr_size += ele[index:]
                index = 0
                try:
                    ele = next(stream) #get the next chunk
                except:
                    return #this means the stream is over and to break out of the generator
        while not get_size: #looking for the next file of a specific size
            next_ind = index + size - len(curr_file) #the next index if you're trying to get the entire file
            if next_ind <= len(ele): #the rest of the file or the whole file is in the chunk
                curr_file += ele[index:next_ind] #getting the rest of the file
                yield curr_file #yielding it
                #resetting varaibles
                get_size = True
                index = next_ind
                curr_file = b''
            else: #look in the next chunk for the rest of the file
                curr_file += ele[index:]
                index = 0
                try:
                    ele = next(stream)
                except:
                    return #breaks out of the generator when the generator object is finished
    
        
        
    
if __name__ == "__main__":
    '''
    url = sys.argv[1]
    file = open(sys.argv[2], 'wb')
    x=1
    for ele in files_from_sequence(download_file(url)):
        #file.write(ele)
        if x == 53:
            file.write(ele)
        x+=1
    '''
    pass
        
 