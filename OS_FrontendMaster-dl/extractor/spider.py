from bs4                             import BeautifulSoup
from selenium                        import webdriver
from selenium.webdriver.common.keys  import Keys
from urllib2                         import urlopen, URLError, HTTPError
from helper                          import *

import httplib
import cookielib
import json
import mechanize
import os
import time

# Constants
DATA_COURSE_LIST              = './DATA_COURSE_LIST.json'
DATA_COURSE_DETAILED_LIST_CDN = './DATA_COURSE_DETAILED_LIST_CDN.json'
URL_LOG_IN                    = 'https://frontendmasters.com/login/'
URL_COURSE_LIST               = 'https://frontendmasters.com/courses/'

class Spider(object):
    def __init__(self, mute_audio):
        options = webdriver.ChromeOptions()

        # FM detects useragent and says 403 as return
        # so we just define valid useragent
        options.add_argument('--no-sandbox')
        options.add_argument("--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

        if mute_audio:
            options.add_argument("--mute-audio")

        self.browser = webdriver.Chrome(chrome_options=options)

    def login(self, id, password):
        self.browser.get(URL_LOG_IN)
        time.sleep(2)

        username_field = self.browser.find_element_by_id('username')
        password_field = self.browser.find_element_by_id('password')

        username_field.send_keys(id)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

    def download(self, course, high_resolution, video_per_video):
        if self.browser.find_elements_by_class_name('Message'):
            print "Your username/password was incorrect"
            exit(1)
        # Get detailed course list
        course_detailed_list = self._get_detailed_course_list(course)

        # Get downloadable CDN
        course_downloadbale = self._get_downloadable_links(course_detailed_list, high_resolution, video_per_video)

        # Download course videos
        if not video_per_video:
            self.download_course(course_downloadbale)

        # self.browser.close()


    def _get_detailed_course_list(self, course):
        course_link = URL_COURSE_LIST + course + '/'
        course_detial = {
            'title': course,
            'url': course_link,
            'sections': []
        }

        self.browser.get(course_link)
        self.browser.implicitly_wait(2)
        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')

        # Find video nav list
        sections = soup_page.find('section', {'class': 'CourseToc'})
        sections_items = sections.find_all(
            'ul', {'class': 'LessonList'}
        )

        sections = self._get_section_data(sections_items)
        course_detial['sections'].extend(sections)

        return course_detial

    def _get_section_data(self, sections_items):
        sections = []

        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        titles = soup_page.find('section', {'class': 'CourseToc'}).find_all('h2', {'class', 'lessongroup'})

        for index, item in enumerate(sections_items, start=0):
            # Course section data structure
            course_section = {
                'title': None,
                'subsections': []
            }

            course_section['title'] = titles[index].getText()

            videos_section = item
            videos_section_items = videos_section.find_all('li')

            videos_data = self._get_videos_data(videos_section_items)
            course_section['subsections'].extend(videos_data)

            sections.append(course_section)

        return sections

    def _get_videos_data(self, videos_section_items):
        subsections = []

        for video in videos_section_items:
            # Course subsection data structure
            course_subsection = {
                'title': None,
                'url': None,
                'downloadable_url': None
            }

            course_subsection['url'] = video.find('a')['href']
            title = video.find('a').find(
                'div', {'class', 'heading'}
            ).find(
                'h3', { }
            ).getText()

            course_subsection['title'] = format_filename(title)
            subsections.append(course_subsection)

        return subsections

    def _get_downloadable_links(self, course, high_resolution, video_per_video):
        # course data structure
        # {
        #     'title': course,
        #     'url': course_link,
        #     'sections': []
        # }

        url = course['url']
        title = course['title']
        download_path = self.create_download_directory()
        course_path = self.create_course_directory(download_path, title)

        for i1, section in enumerate(course['sections']):
            section_title = section['title']

            for i2, subsection in enumerate(section['subsections']):
                if subsection['downloadable_url'] is None:

                    file_path_without_extension = \
                        get_local_file_path_without_extension(
                            i1, i2, subsection, section_title, course_path
                        )
                    found_file = find_file(file_path_without_extension)

                    if found_file and is_file_downloaded(found_file):
                        continue

                    print("Retrieving: {0}/{1}/{2}".format(
                        format_filename(course['title']),
                        format_filename(section['title']),
                        format_filename(subsection['title'])))

                    video_url = 'https://frontendmasters.com' + subsection['url']
                    self.browser.get(video_url)
                    time.sleep(8)

                    while self.browser.find_elements_by_class_name('Message'):
                        print "429: You have reached maximum request limit. " \
                              "Sleeping for 15 minutes"
                        time.sleep(15 * 60)
                        self.browser.refresh()
                        time.sleep(10)

                    if high_resolution:
                        big_play_button = self.browser.find_element_by_class_name('vjs-big-play-button')
                        big_play_button.click()
                        resolution_button = self.browser.find_element_by_class_name("fm-vjs-quality")
                        resolution_button.click()

                        high_resolution_text = resolution_button.find_element_by_tag_name("li")
                        high_resolution_text.click()
                        time.sleep(3)

                    url_str = self._get_video_source()
                    print("Video URL: {0}".format(url_str))
                    subsection['downloadable_url'] = url_str
                    if video_per_video:
                        self.download_video(i1, i2, subsection, section_title, course_path)

        return course

    def _get_video_source(self):
        try:
            video_tag = self.browser.find_element_by_tag_name('video')
            source_link = video_tag.get_attribute('src')
            return source_link
        except:
            return "http://placehold.it/500x500"

    def create_download_directory(self):
        download_path = os.path.join(os.path.curdir, 'Download')
        create_path(download_path)
        return download_path

    def create_course_directory(self, download_path, title):
        course_path = os.path.join(download_path, title)
        create_path(course_path)
        return course_path

    def download_course(self, course):
        title = course['title']
        download_path = self.create_download_directory()
        course_path = self.create_course_directory(download_path, title)

        for i1, section in enumerate(course['sections']):
            section_title = section['title']

            for i2, subsection in enumerate(section['subsections']):
                self.download_video(i1, i2, subsection, section_title, course_path)

    def download_video(self, i1, i2, subsection, section_title, course_path):
        subsection_title = subsection['title']
        print("Downloading: {0}".format(
            format_filename(subsection_title)))

        file_path = get_local_file_path(
            i1, i2, subsection, section_title, course_path
        )

        download_file(subsection['downloadable_url'], file_path)
