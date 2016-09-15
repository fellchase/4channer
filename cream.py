'''
4chan Media Downloader v1.0 BETA
Codename: Cream

This script can download all videos, images and gifs in a 4chan Thread(s).
Images and Gifs are optional to download.

Coded in: Py 3.5; Developed for Windows Command Prompt
'''

import requests, sys, re, os, time
from codecs import *
from bs4 import BeautifulSoup


URL = "https://boards.4chan.org/gif"  # Default URL

downloadGif = False
downloadImage = False
multiThread = False
webFile = False

sizeCount = 0  
dlVidCount = 1  # Used to record videos downloaded
counter = 1  # used in founder function to record number of videos found
totalBytesDownloaded = 0
totalTime = 0.0
operationTime = time.time()
directory = os.getcwd()

regex_notwebpage = re.compile(r'(?!\.asp|\.aspx|\.jsp|\.php|\.html)\.\w+\b$')
regex_Resolution = re.compile(r'File: .+ \(.+, (\w+)\)')

myheaders = {'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}

class Video:
    '''
    Video class represents a media to be downloaded, 
    It can be a 4chan video or image or any regular file on web.
    '''
    def __init__(self, URL, filename, videoSize, resolution, sizeCount=0):
        self.resolution = resolution
        self.URL = URL
        self.sizeCount = sizeCount # sizeCount = 0 means that a thread is given when only a file
        self.videoSize = videoSize
        self.filename = filename

    def timeStamp(self, sizeCount, totalBytesDownloaded, averageSpeed):
        timeleft = ((int(sizeCount) - totalBytesDownloaded) // 1024) // averageSpeed # Time Left To complete in Seconds
        return time.strftime("%H:%M:%S", time.gmtime(timeleft))

    def printDlStats(self, downloadPercentage, filename, kiloBytesDownloaded, videoSize, averageSpeed):
        global totalBytesDownloaded
        if self.sizeCount:
            uprint(str(downloadPercentage) + "%", os.path.basename(filename), "[" + str(kiloBytesDownloaded), "KB/" + str(int(videoSize) // 1024)
            , "KB]", averageSpeed, 'Kbps Time Left -', self.timeStamp(self.sizeCount, totalBytesDownloaded, averageSpeed), end='\r')
        else:
            uprint(str(downloadPercentage) + "%", os.path.basename(filename), "[" + str(kiloBytesDownloaded), "KB/" + str(int(videoSize) // 1024)
            , "KB]", averageSpeed, 'Kbps Time Left -', self.timeStamp(int(videoSize), kiloBytesDownloaded*1024, averageSpeed), end='\r')

    printDledStats = lambda self:    uprint(dlVidCount, 'of', counter - 1, "Saved..", os.path.abspath(self.filename), "[" + str(int(self.videoSize) // 1024), "KB]")

    def download(self):
        global totalBytesDownloaded, totalTime, dlVidCount
        bytesDownloaded = 0
        response = requests.get(self.URL, headers=myheaders, stream=True)
        response.raise_for_status()
        start = time.clock()
        while True:
            try:
                if os.path.isfile(self.filename):
                    if os.path.isfile(os.path.join(os.path.dirname(self.filename), self.URL.split('/')[-1])):
                        self.filename = os.path.join(os.path.dirname(self.filename), self.URL.split('/')[-1].split('.')[0] + '[1].' + self.URL.split('/')[-1].split('.')[-1])
                        fp = open(self.filename, 'wb+')
                    else:
                        self.filename = os.path.join(os.path.dirname(self.filename), self.URL.split('/')[-1])
                        fp = open(self.filename, 'wb+')
                else:
                    fp = open(self.filename, 'wb+')
                break
            except FileNotFoundError:
                os.makedirs(os.path.dirname(self.filename))
        uprint('\nFile..', self.URL, "of", '(' + self.resolution + ')')
        for chunk in response.iter_content(50 * 1024):  # 50 KB per iteration
            timeGap = time.clock() - start  # Time for a video
            totalTime += timeGap  # Total time of session
            bytesDownloaded += len(chunk)  # Bytes of video
            totalBytesDownloaded += len(chunk)  # bytes downloaded since start of session

            downloadPercentage = int((bytesDownloaded / int(self.videoSize)) * 100)
            kiloBytesDownloaded = bytesDownloaded // 1024
            averageSpeed = int(float(totalBytesDownloaded // 1024) / totalTime) # Average Speed in KB/s
            self.printDlStats(downloadPercentage, self.filename, kiloBytesDownloaded, self.videoSize, averageSpeed)

            if chunk:
                fp.write(chunk)
            start = time.clock()
        fp.close()
        self.printDledStats()
        dlVidCount += 1


class Thread:
    '''
    Thread represents a 4chan Thread or a board.
    '''
    def __init__(self, URL, downloadGif, downloadImage):
        self.URL = URL
        self.downloadGif = downloadGif
        self.downloadImage = downloadImage

    def subLister(self, element):
        # This creates Tuples for downloadLister Function which adds them in array
        global sizeCount
        href = str('https:' + element.a.get('href'))
        textAnchor = str(element.a.getText())

        try:
            length = requests.head(url=href).headers['content-length']
            sizeCount += int(length)
        except:
            length = 0
        try:
            resolution = regex_Resolution.search(element.getText()).group(1)
        except:
            resolution = 'Unknown'
        return href, textAnchor, length, resolution

    def downloadLister(self):
        # Creates a Array of Tuples for downloadVideo function
        downloadList = []
        response = requests.get(self.URL, headers=myheaders)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select('.fileText')
        ballsgif = 'i.4cdn.org/gif/1397912081601.gif'

        for element in elements:     # Each element bearing 'fileText'
            hyperlink = element.a.get('href')
            if ballsgif in hyperlink:
                continue
            if hyperlink.endswith('.gif'):    # Whether file is gif or not
                if self.downloadGif:
                    downloadList.append(self.subLister(element))
                else:
                    continue
            # Whether file is a image or not
            elif hyperlink.endswith('.jpg') or hyperlink.endswith('.png') or hyperlink.endswith('.jpeg'):
                if self.downloadImage:
                    downloadList.append(self.subLister(element))
                else:
                    continue
            else:   # This means it's a .webm or other media file
                downloadList.append(self.subLister(element))
        return downloadList


def founder(theList): # Finds videos in the thread
    global counter
    for i in theList:
        uprint("[" + str(counter) + "]", i[0], i[1], str(int(i[2]) // 1024), "KB (" + i[3] + ")\n")
        counter += 1


def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    # Unicode Print
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


print('''
============================= INSTRUCTIONS ================================
To download 4chan Thread Enter its URL don't forget / at end 
for example https://www.google.com/
*Does not work when asked for CAPTCHA, use VPN
To download Multiple Threads Enter URLs separated by commas,
Ensure that you do not put spaces around commas.
https://boards.4chan.org/thread/12345,https://boards.4chan.org/thread/67890
To download a single file enter its URL, ensure it has its extension
>>> https://dl.example.com/example.mp4
You can not download multiple files simultaneously.
Default URL is https://4chan.org/gif
To download latest content from gif board, Press Enter
''')

rawURL = input("Enter URL(s): ").strip()
rawDirectory = os.path.abspath(input("\nWhere do you want to save files? 'Enter' for working directory ").strip('/\\'))

# URL input validation 
if rawURL != "":
    if ',' in rawURL:
        URL = rawURL.split(',')
        multiThread = True
    elif regex_notwebpage.search(rawURL) ==  None: # When given a webpage extention or directory i.e. a Webpage
        URL = rawURL
    elif regex_notwebpage.search(rawURL) !=  None: # Given any kind of file's Webaddreess
        URL = rawURL
        webFile = True
# Directory Input Validation
if rawDirectory != "":
    if os.path.exists(rawDirectory):
        directory = rawDirectory
        os.chdir(os.path.abspath(directory))
    else:
        print('Making Directories...', rawDirectory)
        directory = rawDirectory
        print("Directory:", os.path.abspath(directory))

if webFile == False:
    if input("\nDo you want to download GIFs? 'Y' or 'Enter' to skip\n") != "":
        downloadGif = True
    if input("Do you want to download Images? 'Y' or 'Enter' to skip\n") != "":
        downloadImage = True

# Downloader
try:
    if webFile:  # A regular file
        videoSize = requests.head(url=URL).headers['content-length']
        video = Video(URL, URL.split('/')[-1], videoSize, 'Unknown Resolution')
        video.download()
    elif multiThread:  # More than one thread
        allThreads = []
        for i in URL:
            print('Loading Thread...', i)
            print()
            thread = Thread(i, downloadGif, downloadImage)
            stuffToDownload = thread.downloadLister()
            founder(stuffToDownload)
            if len(stuffToDownload) > 0:
                allThreads.append(stuffToDownload)
            if len(stuffToDownload) == 0:
                print('No Results for ' + i, '\n')
        if len(allThreads) == 0:
                print('Found nothing... Quitting')
                quit()
        if input("\n'Enter' to Download or 'n' to skip download of " + str(counter - 1) + " video(s) of " + str(sizeCount // 1024) + " KB? ") == "":
            for thread, respectiveURL in zip(allThreads, URL):
                for vidInfo in thread:
                    video = Video(vidInfo[0], os.path.join(directory.strip('/\\'), os.path.basename(respectiveURL.strip('/\\')), vidInfo[1].strip('/\\')), vidInfo[2], vidInfo[3], sizeCount)
                    video.download()

            print("\nSuccessfully Downloaded", counter - 1, "file(s) of ", sizeCount // 1024, "KB")
        else:
            print('\nYou cancelled download of', counter - 1, "file(s) of ", sizeCount // 1024, "KB")
    else:  # Single Thread
        print('Loading... ' + URL + '\n')
        thread = Thread(URL, downloadGif, downloadImage)
        stuffToDownload = thread.downloadLister()
        founder(stuffToDownload)
        if len(stuffToDownload) == 0:
            print('No Results for ' + URL)
            print('Quitting')
            quit()
        if input("\n'Enter' to Download or 'n' to skip download of " + str(counter - 1) + " file(s) of " + str(sizeCount // 1024) + " KB? ") == "":
            for i in stuffToDownload:
                video = Video(i[0], os.path.join(directory.strip('/\\'), os.path.basename(URL.strip('/\\')), i[1].strip('/\\')), i[2], i[3], sizeCount)
                video.download()
            print("\nSuccessfully Downloaded", counter - 1, "file(s) of ", sizeCount // 1024, "KB")
        else:
            print('\nYou cancelled download of', counter - 1, "file(s) of ", sizeCount // 1024, "KB")
    print('\nOperation Completed in', time.strftime("%H:%M:%S", time.gmtime(time.time() - operationTime)))
except KeyboardInterrupt:
    print('4chan Media Downloader Stopped')
except Exception as err:
    print(err)
