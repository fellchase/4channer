#                             ____________________________________________________________ 
#                            |                                  _                         |
#                            | |_| _|_  _  _   |\/| _  _|. _   | \ _    _ | _  _  _| _  _ |
#                            |   |(_| |(_|| |  |  |(/_(_||(_|  |_/(_)VV| ||(_)(_|(_|(/_|  |
#                            | --------------------------- v2 --------------------------- |
#                            |            https://github.com/fellchase/4channer/          |
#                            |                                                            |
#                            |              Cross Platform 4chan Downloader               |
#                            |   Download Multiple threads with Videos, GIFs and Images   |
#                            |   Written by fellchase in Python 3 -- Dependencies : bs4   |
#                            |____________________________________________________________|


try:
    from urllib import request as req
    from sys import stdout, argv, platform
    from time import strftime, gmtime, time
    from os import get_terminal_size, makedirs
    from os.path import join, abspath, isdir, isfile, dirname, basename
    from bs4 import BeautifulSoup
except ImportError as import_error:
    print(import_error)
    print("Dependencies : Python Standard Library & bs4")
    print("Missing modules aren't in this folder, get them here -> https://github.com/fellchase/4channer")
    quit("Otherwise download them with pip --> https://docs.python.org/3.6/installing/")


try:
    columns, rows = get_terminal_size()
    if platform == 'win32':
        columns -= 1  # Because Windows CMD is -_- It adds new lines otherwise and ruins everything
except OSError:  # Error usually raised when script isn't running in CMD or terminal, it can be running in an IDE
    columns, rows = (79, 24)  # Numbers are arbitrarily assigned
    print("CLI not recognized, arbitrarily assigning character limits to columns -->", columns, "& rows -->", rows)


if 'help' in argv:  # Help banner
    print(" ____________________________________________________________ ".center(columns))
    print("|                                  _                         |".center(columns))
    print("| |_| _|_  _  _   |\/| _  _|. _   | \ _    _ | _  _  _| _  _ |".center(columns))
    print("|   |(_| |(_|| |  |  |(/_(_||(_|  |_/(_)VV| ||(_)(_|(_|(/_|  |".center(columns))
    print("| --------------------------- v2 --------------------------- |".center(columns))
    print("|                   How to use 4channer.py?                  |".center(columns))
    print("|                                                            |".center(columns))
    print("| [1] http-only -- Forces to use HTTP instead of HTTPS       |".center(columns))
    print("| It's used in case of SSL: CERTIFICATE_VERIFY_FAILED error  |".center(columns))
    print("|                                                            |".center(columns))
    print("| [2] help -- Displays this help text                        |".center(columns))
    print("|                                                            |".center(columns))
    print("| URL entered must have either 'http://' or 'https://' in it |".center(columns))
    print("|           Multiple URLs must be separated by ','           |".center(columns))
    print("|                                                            |".center(columns))
    print("|                 HTTPS is used by default                   |".center(columns))
    print("|     Try using VPN if script is unable to find anything     |".center(columns))
    print("|                                                            |".center(columns))
    print("| Options given in square brackets are selected by default   |".center(columns))
    print("| Just hit ENTER, similarly hit ENTER to select capitalized  |".center(columns))
    print("|                 options in [Y/n] questions                 |".center(columns))
    print("|____________________________________________________________|".center(columns))
    quit()

# This Banner is always displayed
print(" ____________________________________________________________ ".center(columns))
print("|                                  _                         |".center(columns))
print("| |_| _|_  _  _   |\/| _  _|. _   | \ _    _ | _  _  _| _  _ |".center(columns))
print("|   |(_| |(_|| |  |  |(/_(_||(_|  |_/(_)VV| ||(_)(_|(_|(/_|  |".center(columns))
print("| --------------------------- v2 --------------------------- |".center(columns))
print("|            https://github.com/fellchase/4channer/          |".center(columns))
print("|                                                            |".center(columns))
print("|              Cross Platform 4chan Downloader               |".center(columns))
print("|   Download Multiple threads with Videos, GIFs and Images   |".center(columns))
print("|   Written by fellchase in Python 3 -- Dependencies : bs4   |".center(columns))
print("| ---------------------------------------------------------- |".center(columns))
print("|       python 4channer.py help for usage instructions       |".center(columns))
print("|____________________________________________________________|".center(columns))
print()


# In case of SSL: CERTIFICATE_VERIFY_FAILED error
if "http-only" in argv:
    protocol = 'http'
    print("Using HTTP".center(columns))
else:
    protocol = 'https'

URL = protocol + "://boards.4chan.org/wg/"
script_directory = dirname(abspath(__file__))  # Files are saved in script's directory, but it can be changed

total_session_dl_size = 0  # Combined size of all items that may be downloaded in bytes
session_dl_so_far = 0  # Combined size of items which have been downloaded so far in bytes
time_since_dl_started = 0  # Time since download of items started in seconds


def make_flat_list(input_list):
    """Takes a multidimensional list and returns a one dimensional list"""
    flat_list = []

    for x in input_list:
        if type(x) != list:
            flat_list.append(x)
        elif type(x) == list:
            for y in make_flat_list(x):
                flat_list.append(y)
    
    return flat_list


def uprint(*objects, sep=' ', end='\n', file=stdout):
    """Unicode Print"""
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


def fit_str(str_to_fit, rest_of_string):
    """
    Shrinks str_to_fit if it's too long and space isn't available on command line, returns str_to_fit after making
    modifications if necessary
    """
    len_of_str_available = abs(columns - len(rest_of_string) - 1)  # Max space available for str_to_fit; -1 for safety

    if len(str_to_fit) > len_of_str_available:  # We shrink str_to_fit If length is more than len_of_str_available
        beginning_half = str_to_fit[:(len_of_str_available // 2) - 3]  # Less 3 chars, we be add three periods later
        ending_half = str_to_fit[-(len_of_str_available // 2):]  
        str_to_fit = beginning_half + '...' + ending_half  

    return str_to_fit


def alpha_numeric_filter(string):
    """Takes a string and returns a filtered string with only alpha-numeric characters"""
    filtered = ""

    for char in string:
        if char.isalnum() or char == ' ':
            filtered += char
        if char == '\n':
            continue

    return filtered


def get_web_page_source(url):
    """Takes url of webpage and gets source code for that webpage, also prints size of webpage downloaded"""
    html_dled = 0  # Used to find percentage of page downloaded
    source_html = ""  
    request = req.Request(url)  # Framing a request
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 '
                                     '(KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')
    
    print('Awaiting response from', url)

    # Sends request to server
    response = req.urlopen(request)

    if response.getcode() == 200:
        print("HTTP Response Status Code 200 OK")
    else:
        print("HTTP Response Status Code", response.getcode())

    # Reads response in chunks and flushes it to source_html
    while True:
        buffer = response.read(1024 * 50).decode('utf-8')  # Converts the chunk from byte string to plain text
        if not buffer:
            break
        
        source_html += buffer  # Adding parts of response to source_html to return
        html_dled += len(buffer)  # Bytes being downloaded added to calculate percentage

        print("Fetching Response from {} [ {} kB ]".format(url, html_dled // 1024), end='\r')

    print()
    # Cleans the current line so that text from previous print statement gets deleted. \r doesn't leave a line
    print(' ' * columns, end='\r') 

    return source_html


def info_of_each_item(element, thread_name):
    """
    Takes element tag from make_download_list and returns tuples
    Tuples are structured in this way ('href', 'remote_file_name', 'size_in_bytes')
    REMOTE FILE NAME also has thread name with it like this => linuxthread/linux.webm

    :param element:
    Example of element with class="fileText" which is passed as param

    <div class="fileText" id="fT10316269">File: <a href="//i.4cdn.org/wg/1489266570954.jpg" target="_blank"
    title="a very very very very long file name.webm">a very very very ve(...).webm</a>
    (2.54 MB, 640x480)</div>

    :param thread_name:
    thread_name serves as directory name later on.
    """
    global total_session_dl_size  # Keeps track of size of all items to be downloaded

    # Finding href
    href = str(protocol + ':' + element.a.get('href'))  # Adding protocol because its missing, refer example above

    # Finding remote_file_name
    remote_file_name = str(element.a.get('title'))  # Title attribute exists only for long names, but not for short ones

    if remote_file_name == "None":  # Element doesn't have a long name, title attribute is missing
        remote_file_name = str(element.a.getText())  # Short names are found in innerHTML

    # Finding size_in_bytes
    try:
        request = req.Request(href)  # Framing a request
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 '
                                         '(KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17') 
        size_in_bytes = int(req.urlopen(request).info()['Content-Length'])
    except KeyboardInterrupt:
        quit("\nTerminated by user")
    except Exception as e:
        print(e)
        uprint("[INFO] Unable to get proper size, assuming size to be ONE for", remote_file_name)
        size_in_bytes = 1

    total_session_dl_size += size_in_bytes  # Size of each item must be added in total_session_dl_size

    # Processing remote_file_name to filter non alpha numeric characters
    # Splitting remote_file_name into filename and extension
    file_name_list = remote_file_name.split('.')  # ...webm -> ['', '', '', 'webm']
    *file_name, extension = file_name_list  # file_name -> ['', '', ''] extension -> 'webm'

    sanitized_file_name = alpha_numeric_filter('.'.join(file_name))
    sanitized_thread_name = alpha_numeric_filter(thread_name)

    # Joining [Sanitized] thread name and filename with extension -> thread name / filename . end
    remote_file_name = join(sanitized_thread_name, '.'.join((sanitized_file_name, extension)))

    return href, remote_file_name, size_in_bytes


def make_download_list(url):
    """Takes url, calls get_web_page_source() finds thread_name and makes a list of tuples for download_item()"""
    download_list = []
    html = get_web_page_source(url)
    bad_gif = "i.4cdn.org/wg/1489266570954.jpg"  # No need to download this 
    print("Parsing response...")
    soup = BeautifulSoup(html, 'html.parser')

    elements_with_fileText = soup.select('.fileText')  # All elements with class=fileText
    elements_with_subject = soup.select('.subject')  # All elements with class=subject
    
    # Setting thread_name
    # Zeroth element is always thread name => <span class="subject">Thread Name</span>
    thread_name = elements_with_subject[0].getText()

    # If thread has no name there are following options
    if url.find('thread') == -1:  # It's not a thread, but it can be a board URL => https://boards.4chan.org/g/
        thread_name = soup.select('.boardTitle')[0].getText()  # Try to get title of the board
    elif thread_name == '':  # Board has no title, comment on thread is secondary option
        result = soup.find("blockquote", {"class": "postMessage"})  # Comment's element tag
        thread_name = result.text[:10]  # Only ten characters since beginning of comment

    # Sorting the download_list and passing thread_name to prepend it to item's name
    for count, element in enumerate(elements_with_fileText):  # Each element bearing 'fileText'
        hyperlink = element.a.get('href')
        if bad_gif in hyperlink:
            continue
        if hyperlink.endswith('.gif'):
            if download_gif:
                download_list.append(info_of_each_item(element, thread_name))
            else:
                continue
        elif hyperlink.endswith('.jpg') or hyperlink.endswith('.png') or hyperlink.endswith('.jpeg'):
            if download_image:
                download_list.append(info_of_each_item(element, thread_name))
            else:
                continue
        else:   # It's a .webm or other media file
            download_list.append(info_of_each_item(element, thread_name))

        # Variable count starts from 0, hence we need to add 1 to count
        print("Making Download List {:.2%}".format((count + 1) / len(elements_with_fileText)), end='\r')
    print(' ' * columns)  # Clears last printed line
    return download_list


def print_found_items(download_list):
    """
    Prints items in download_list
    download_list contains tuples, tuples are structured this way -- ('href', 'remote_file_name', 'size_in_bytes')
    remote_file_name also has thread name with it like this => linuxthread/linux.webm
    """
    print('Download List'.center(columns, '-'))
    print()
    for i, item in enumerate(download_list):
        uprint('\n[{0}] {2} \n{1} of {3} kB'.format(i + 1, item[0], item[1], item[2] // 1024))  # Bytes to kB
    print()
    print("-" * columns)
    print()


def post_download_stats(name, size): 
    """Prints stats after downloading of item is completed"""
    uprint('Saved {} of {} kB'.format(name, size // 1024))
    print('-' * columns)


def print_download_stats(name, itemdl, total_item_size):
    """Prints stats while item is being downloaded"""
    global time_since_dl_started
    if int(time_since_dl_started) == 0:  # Some weird bug, temporary patch for ZeroDivisionError
        time_since_dl_started = 1
    percent = session_dl_so_far / total_session_dl_size
    spd_in_bps = session_dl_so_far / time_since_dl_started
    eta = (total_session_dl_size - session_dl_so_far) // spd_in_bps  # Time Left To complete in seconds
    string_of_eta = strftime("%H:%M:%S", gmtime(eta))  # Formatted in HH:MM:SS
    name = basename(name)  # name also contains thread name, it's removed here

    str_wo_name = '{percent:.2%}  {itemdl} kB/{total_item_size} kB | {spd} kB/s - {string_of_eta}'.format(
            percent=percent, itemdl=itemdl // 1024, total_item_size=total_item_size // 1024,
            spd=int(spd_in_bps / 1024), string_of_eta=string_of_eta)  # Required for fit_str function 

    uprint('{percent:.2%} {name} {itemdl} kB/{total_item_size} kB | {spd} kB/s - {string_of_eta}'.format(
        percent=percent, name=fit_str(name, str_wo_name), itemdl=itemdl // 1024,
        total_item_size=total_item_size // 1024, spd=int(spd_in_bps / 1024), string_of_eta=string_of_eta), end='\r')


def download_item(href, remote_name, item_size):
    """Takes item information to download an item at a time, also calls print_download_stats(), post_download_stats()"""
    global session_dl_so_far, time_since_dl_started

    request = req.Request(href)  # Framing a request
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 '
                                     '(KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')
    response = req.urlopen(request)  
    local_path = join(script_directory, remote_name)  # remote_name contains thread name in it

    uprint('File {} from {}'.format(remote_name, href))  # Information about file currently being processed

    # Checks if file exists, if so adds "[1]" in its name & if directory doesn't exists it's created
    while True:
        try:
            if isfile(local_path):  # True if exists and is a file, False otherwise
                split_dirname = dirname(local_path)  # /dir/dir
                split_basename = basename(local_path)  # something.txt
                name, extension = split_basename.split('.')  # ('something', 'txt')
                name += "[1]"  # something[1]

                # Joining everything together
                local_path = join(split_dirname, '.'.join((name, extension)))  # ('/dir/dir', ('something[1]', 'txt'))
                continue  # To check if the new local_path still exists or not
            else:
                fp = open(local_path, 'wb')
                break
        except FileNotFoundError:
            makedirs(dirname(local_path))

    start = time()
    item_downloaded = 0
    while True:
        buffer = response.read(1024 * 50)
        if not buffer:
            break

        time_since_dl_started += time() - start  
        item_downloaded += len(buffer)  
        session_dl_so_far += len(buffer)  # Data we got in entire session

        fp.write(buffer)  # Flush the buffer into the file
        print_download_stats(remote_name, item_downloaded, item_size)
        start = time()  # Variable start is reassigned, so to find the time taken to get the response in next iteration

    fp.close()
    post_download_stats(local_path, item_size)


# Taking Input and downloading

try:
    # Sets URL
    print("\nEnter URL(s) [ {0} ]  ".format(URL), end='')
    custom_user_url = input().strip(' ')
    if custom_user_url != '':  # Custom URL given
        # Checking for multiple URLs or single url
        if len(custom_user_url.split(',')) == 1:  # One URL is given
            # Remove whatever protocol is given in input and replace it with proper protocol
            if custom_user_url.find('https') != -1:
                custom_user_url = custom_user_url.replace('https', protocol)
            else:
                custom_user_url = custom_user_url.replace('http', protocol)
            URL = custom_user_url
        elif len(custom_user_url.split(',')) > 1:  # More than one URL is given
            URL = []  # Changed to be an list, because append method is only avaiable for lists
            for item in custom_user_url.split(','):
                # Remove whatever protocol is given in input and replace it with proper protocol
                if item.find('https') != -1:
                    item = item.replace('https', protocol)
                else:
                    item = item.replace('http', protocol)
                URL.append(item.strip(' '))

    # Sets download_gif boolean value
    print("Do you want to download GIFs? [Y/n]  ", end='')
    download_gif_answer = input().strip(' ').lower()
    if download_gif_answer == 'y' or download_gif_answer == '':
        download_gif = True
    elif download_gif_answer == 'n':
        download_gif = False
    else:
        quit("Incorrect input --> " + download_gif_answer)

    # Sets download_image boolean value
    print("Do you want to download Images? [Y/n]  ", end='')
    download_image_answer = input().strip(' ').lower()
    if download_image_answer == 'y' or download_image_answer == '':
        download_image = True
    elif download_image_answer == 'n':
        download_image = False
    else:
        quit("Incorrect input --> " + download_image_answer)

    # Sets path
    print("Where to save files? (Enter Full Path)\n[" + script_directory + "]  ", end='')
    custom_user_path = input().strip(' ')

    if custom_user_path == "":
        custom_user_path = script_directory  # If nothing is entered user wants files to be in script directory
    elif custom_user_path != "":  # User has supplied his custom path
        custom_user_path = abspath(custom_user_path.rstrip('/\\'))
        if isdir(custom_user_path) == False:  # Path does not exists
            uprint(custom_user_path, "does not exists, create it? [Y/n]  ", end='')
            path_answer = input().strip(' ')
            if path_answer == "" or path_answer == "Y":
                makedirs(custom_user_path)  # Path created
                uprint("Created Directory", custom_user_path)
            elif path_answer == "n":
                quit('Terminating')  # Path wasn't created and we quit
            else:
                quit("Incorrect input --> " + path_answer)
        else:  # Path Exists
            uprint("Path already exists -->", custom_user_path)
        script_directory = custom_user_path

    uprint("Path Set to -->", script_directory)
    print('-' * columns)

    # Downloader

    if type(URL) == str:  # Single URL
        dl_list = make_download_list(URL)

        if len(dl_list) == 0:
            quit("There's nothing to download")

        print_found_items(dl_list)

        uprint("Continue download of {} item(s) of {} kB at {} ? [Y/n]  ".format(
            len(dl_list), total_session_dl_size // 1024, script_directory), end='')

        download_input = input().strip(' ')
        print()
        if download_input == "Y" or download_input == "":
            for item in dl_list:
                download_item(*item)
            quit('Done')
        elif download_input == 'n':
            quit('You chose not to proceed')
        else:
            quit("Incorrect input --> " + download_input)

    elif type(URL) == list:  # Multiple URLs are given
        dl_lists = []

        [dl_lists.append(make_download_list(single_url)) for single_url in URL]  # Appends a download list to dl_lists
        dl_lists = make_flat_list(dl_lists)  # Flattening the list because it has more than one list inside it

        if len(dl_lists) == 0:
            quit("There's nothing to download")

        print_found_items(dl_lists)

        uprint("Continue download of {} item(s) of {} kB at {} ? [Y/n]  ".format(
            len(dl_lists), total_session_dl_size // 1024, script_directory), end='')
        
        download_input = input().strip(' ')
        print()
        if download_input == "Y" or download_input == "":
            for item in dl_lists:
                download_item(*item)
            quit('Done')
        elif download_input == 'n':
            quit('You chose not to proceed')
        else:
            quit("Incorrect input --> " + download_input)

except ConnectionAbortedError:
    quit('Connection was aborted by server')
except ConnectionRefusedError:
    quit('Connection was refused by server')
except ConnectionResetError:
    quit('Connection is reset by server')
except PermissionError:
    quit("You do not have permission to save files at " + script_directory)
except req.HTTPError as http_error:
    if '404' in str(http_error):
        quit('Requested page does not exists')
    quit(http_error)
except req.URLError as url_error:
    if 'service not known' in str(url_error) or 'getaddrinfo failed' in str(url_error):
        quit("Server not found, check your network connection or check the address")
    if 'SSL: CERTIFICATE_VERIFY_FAILED' in str(url_error):
        print(url_error)
        quit("Rerun the script with http-only argument & see if the error still persist\nex. python 4channer.py http-only")
    quit(url_error)
except KeyboardInterrupt:
    quit("\nTerminated by user")
except Exception as err:
    print("UNKNOWN ERROR OCCURRED")
    quit(err)
