import glob
import os
import os.path
import string
from urllib2 import urlopen, URLError, HTTPError

def format_filename(filename_str):
    s = filename_str
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


def get_local_file_path(i1, i2, subsection, section_title, course_path):
    extension = get_file_path_from_url(subsection['downloadable_url'])

    return get_local_file_path_without_extension(
        i1, i2, subsection, section_title, course_path
    ) + '.' + extension


def get_local_file_path_without_extension(
        i1, i2, subsection, section_title, course_path
):
    filename = str(i1) + '-' + str(i2) + '-' + format_filename(section_title)\
               + '-' + format_filename(subsection['title'])

    return os.path.join(course_path, format_filename(filename))


def find_file(path_without_extension):
    found_files = glob.glob("%s.*" % path_without_extension)

    return found_files[0] if found_files else None


def is_file_downloaded(path):
    return os.path.isfile(path) and os.path.getsize(path) != 0


def get_file_path_from_url(url):
    return url.split("?")[0].split(".")[-1]

def download_file(url, path):
    if url is None:
        return
    if len(url) <= 1:
        return

    if not is_file_downloaded(path):
        buff = urlopen(url)
        print("Downloading: %s" % (path))
        
        try:
            with open(path, 'wb') as local_file:
                local_file.write(buff.read())
        except Exception as err:
            print(err)



def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
