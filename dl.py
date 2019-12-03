from urllib import request
import sys
from bs4 import BeautifulSoup as bs # parse webpage to get links
import re # regex for filtering links
from urllib.parse import urlparse
import shutil # get console width
import time # time operation
import argparse

# if len(sys.argv) < 2:
#     print("Please provide a link")
#     sys.exit(0)

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
parser._action_groups.append(optionalArgs)
args = parser.parse_args()

startT = time.time_ns()
response = request.urlopen(args.link)
if response.getcode() != 200:
    print("Error opening website, website returned ", response.getcode())
    sys.exit(response.getcode())
url = response.geturl()
page = response.read()
soup = bs(page,"html.parser")
links=[]
fileTypes = args.types
fileRegex = re.compile('^.*\.('+ fileTypes + ')$', re.IGNORECASE) # match all file types included
urlRegex = re.compile('^.+:\/\/.+$') # match [ANYTHING]://[ANYTHING]
for linkObj in soup.findAll('a'):
    link = linkObj.get('href')
    # is string and matches file type link
    if isinstance(link, str) and fileRegex.match(link) != None: 
        if urlRegex.match(link) == None:
            link = url+link # some links I worked with have accidental root links (instead of local relative ones), that's when this line is helpful instead of the following
            # if link[0] != '/': #put together absolut directories
            #     link = url+link
            # else:
            #     parsedUrl = urlparse(url)
            #     link = parsedUrl.scheme + '://' + parsedUrl.netloc + link # root directory
        links.append(link)
        if args.list:
            print(link)
try:
    saveDir = args.dir
    if saveDir[-1] != '/':
        saveDir += '/'
    consoleWidth = shutil.get_terminal_size((80, 20)).columns
    for i, link in enumerate(links):
        i+=1
        start = link.rindex('/')+1
        if start == -1:
            start = 0 # start from beginning if just file name is in the link
        fileName = link[start:]
        progress = ("%.2f%% (%d/%d)" % ((i/len(links))*100, i, len(links))).rjust(consoleWidth-1) # leave space for reset character
        prompt = "Downloading %s" % fileName
        if len(prompt) > len(progress):
            combined = prompt
        else:
            combined = prompt + progress[len(prompt):]
        print(combined, end='\r', flush=True)
        request.urlretrieve(link, saveDir+fileName)

    endT = time.time_ns()
    finishText = 'All Done! Downloaded %d files. Took %.2fs.' % (len(links), (endT-startT)*1e-9) 
    print(finishText + " "*(consoleWidth-len(finishText)))
except Exception as e:
    print(e)
    sys.exit(-1)