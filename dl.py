from urllib import request
import sys
import os
from bs4 import BeautifulSoup as bs # parse webpage to get links
import re # regex for filtering links
from urllib.parse import urlparse
import shutil # get console width
import time # time operation
import argparse
from multiprocessing.pool import ThreadPool

def getFileName(link):
    start = link.rindex('/') + 1
    if start == -1:
        start = 0  # start from beginning if just file name is in the link
    return link[start:]

def printProgress(i, fileName, finished=False):
    progress = ("%.2f%% (%d/%d)" % ((i / len(links)) * 100, i, len(links))).rjust(
        consoleWidth - 1)  # leave space for reset character
    if finished:
        prompt = "Downloaded %s" % fileName
    else:
        prompt = "Downloading %s" % fileName
    if len(prompt) > len(progress):
        combined = prompt
    else:
        combined = prompt + progress[len(prompt):]
    print(combined, end='\r', flush=True)
    return fileName


def downloadFile(saveDir, link, fileName = None):
    if fileName is None:
        fileName = getFileName(link)
    request.urlretrieve(link, saveDir + fileName)  # download
    return fileName


# argument parsing part
parser = argparse.ArgumentParser(description='Tool for batch downloading files from links on a given web page')
optionalArgs = parser._action_groups.pop() 
optionalArgs.title = 'Optional Arguments'
requiredArgs = parser.add_argument_group('Required Arguments')
requiredArgs.add_argument('link', metavar='URL',
                    help='Link to the web page to download from')               
optionalArgs.add_argument('-d', '--dir', dest='dir', default='./',
                    help='Directory to save the downloaded files, defaults to current directory')
optionalArgs.add_argument('-t', '--types', dest='types', default='pptx|pdf',
                    help='File types to be downloaded, seperate each with "|", case insensitive')
optionalArgs.add_argument('-l', '--list', dest='list', action='store_true', help='List the downloadable links on the web page')
optionalArgs.add_argument('-m', '--threads', dest='threads', type=int, default=20, help='Specify maximum number of threads to use for download, default is 20, use 1 for single-thread ordered download')
parser._action_groups.append(optionalArgs)
args = parser.parse_args()
# multi-thread 389.41
startT = time.time_ns()
response = request.urlopen(args.link)
if response.getcode() != 200:
    print("Error opening website, website returned ", response.getcode())
    sys.exit(response.getcode())
url = response.geturl()
page = response.read()
soup = bs(page,"html.parser")
links=set() # avoid duplicates
fileTypes = args.types
fileRegex = re.compile('^.*\.('+ fileTypes + ')$', re.IGNORECASE) # match all file types included
urlRegex = re.compile('^.+:\/\/.+$') # match [ANYTHING]://[ANYTHING]
for linkObj in soup.findAll('a'):
    link = linkObj.get('href')
    # is string and matches file type link
    if isinstance(link, str) and fileRegex.match(link) != None: 
        if urlRegex.match(link) == None:
            # link = url+link # some links I worked with have accidental root links (instead of local relative ones), that's when this line is helpful instead of the following
            if link[0] != '/': #put together absolut directories
                link = url+link
            else:
                parsedUrl = urlparse(url)
                link = parsedUrl.scheme + '://' + parsedUrl.netloc + link # root directory
        links.add(link)
        if args.list:
            print(link)
try:
    saveDir = args.dir
    if saveDir[-1] != '/': # complete directory
        saveDir += '/'
    if not os.path.isdir(saveDir): # if save directory doesn't exist
        os.mkdir(saveDir) # create one
    consoleWidth = shutil.get_terminal_size((80, 20)).columns
    if args.threads == 1:  # single-thread
        for i, link in enumerate(links):
            i+=1
            fileName = getFileName(link)
            printProgress(i, fileName)
            downloadFile(saveDir, link, fileName)
    else: # multi-thread
        def downloadAsync(link):
            return downloadFile(saveDir, link)
        results = ThreadPool(args.threads).imap_unordered(downloadAsync, links)
        for i, fileName in enumerate(results):
            i+=1
            printProgress(i, fileName, True)

    endT = time.time_ns()
    finishText = 'All Done! Downloaded %d files. Took %.2fs.' % (len(links), (endT-startT)*1e-9) 
    print(finishText + " "*(consoleWidth-len(finishText)))
except Exception as e:
    print(e)
    sys.exit(-1)