# web-downloader
Tool for batch downloading files from links on a given web page

## Usage
`dl.py [-h] [-d DIR] [-t TYPES] [-l] URL`

Required Arguments:

* URL                   Link to the web page to download from

Optional Arguments:

* `-h, --help`            show help message and exit
  
* `-d DIR, --dir DIR`     Directory to save the downloaded files, defaults to current directory
  
* `-t TYPES, --types TYPES` File types to be downloaded, seperate each with "|", case insensitive
  
* `-l, --list`            List the downloadable links on the web page

## Examples
```
# download into local docs directory
python dl.py https://file-examples.com/index.php/sample-documents-download/sample-pdf-download/ -d docs

# set download type to MP4 files
python dl.py https://file-examples.com/index.php/sample-video-files/sample-mp4-files/ -t mp4

# list downloadable links before downloading
python dl.py https://www.google.com/ -l
```

## External Dependencies
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) (parses web pages)

## To-Do
- [ ] Progress bar for individual files
- [ ] Size display of files
- [ ] Batch renaming of files to be downloaded (e.g. prefix/postfix)
- [ ] Allow user selection of files to download or exclude
- [ ] Download order
