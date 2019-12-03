from urllib import request
import sys
from bs4 import BeautifulSoup as bs # parse webpage to get links
import re # regex for filtering links
from urllib.parse import urlparse
import shutil # get console width
import time # time operation

if len(sys.argv) < 2:
    print("Please provide a link")
    sys.exit(0)

startT = time.time_ns()
response = request.urlopen(sys.argv[1])
if response.getcode() != 200:
    print("Error opening website, website returned ", response.getcode())
    sys.exit(response.getcode())
url = response.geturl()
page = response.read()
soup = bs(page,"html.parser")
links=[]
fileTypes = 'pptx|pdf'
if len(sys.argv) == 4:
    fileTypes = sys.argv[3]
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
        links.append(link)
try:
    for i, link in enumerate(links):
        i+=1
        start = link.rindex('/')+1
        if start == -1:
            start = 0 # start from beginning if just file name is in the link
        fileName = link[start:]
        width = shutil.get_terminal_size((80, 20)).columns
        progress = ("%.2f%% (%d/%d)" % ((i/len(links))*100, i, len(links))).rjust(width-1) # leave space for reset character
        prompt = "Downloading %s" % fileName
        if len(prompt) > len(progress):
            combined = prompt
        else:
            combined = prompt + progress[len(prompt):]
        print(combined, end='\r', flush=True)
        request.urlretrieve(link, fileName)

    endT = time.time_ns()
    finishText = 'All Done! Took %.2fs' % ((endT-startT)*1e-9) 
    print(finishText + " "*(width-len(finishText)))
except Exception as e:
    print(e)
    sys.exit(-1)