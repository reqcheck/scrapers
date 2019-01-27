import webbrowser
import requests
from bs4 import BeautifulSoup
import csv
import re
import json

def page_scrape(all_urls, info_dict):
    iter_urls = iter(all_urls)
    next(iter_urls)
    for url in iter_urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        course_dict = {}
        course_dict['units'] = None
        course_dict['hours'] = None

        subject = soup.select('h1.subject-and-number')[0].text.strip()
        course_dict['subject'] = subject
        name = soup.select('h2.course-title')[0].text.strip()
        course_dict['name'] = name
        if len(soup.select('h3.units')) > 0:
            units = soup.select('h3.units')[0].text.strip()
            course_dict['units'] = units
        if len(soup.select('h3.hours')) > 0:
            hours = soup.select('h3.hours')[0].text.strip()
            course_dict['hours'] = hours

        prereq_list = None
        for ultag in soup.find_all('ul', {'class': 'prereq'}):
            for litag in ultag.find_all('li'):
                if litag.find('a') is not None:
                    prereq_list = ['None']
                    courses = re.findall("[A-Z]{2,4}\s\d\d\d\w?", litag.text)
                    prereq_list.append(courses)
                    del prereq_list[0]
        course_dict['prereqs'] = prereq_list

        coreq_list = None
        for ultag in soup.find_all('ul', {'class': 'precoreq'}):
            for litag in ultag.find_all('li'):
                if litag.find('a') is not None:
                    coreq_list = ['None']
                    courses = re.findall("[A-Z]{2,4}\s\d\d\d\w?", litag.text)
                    coreq_list.append(courses)
                    del coreq_list[0]
        course_dict['coreqs'] = coreq_list

        course_dict['url'] = url
        info_dict[course_dict['subject']] = course_dict

def subject_area_courses_scrape(subject_areas):
    #open the area page
    all_urls = [None]
    for area in subject_areas:
        url = "https://web.uvic.ca/calendar2019-01/CDs/"+area+"/CTs.html"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        tdtag = soup.find_all('td')
        for i in range(0, int(len(tdtag)/2)):
            all_urls.append("https://web.uvic.ca/calendar2019-01/CDs/"+area+"/"+tdtag[i*2].text+".html")

    return all_urls

def subject_area_scrape():
    page = requests.get("https://web.uvic.ca/calendar2019-01/courses/courses-by-subject.html")
    soup = BeautifulSoup(page.text, "html.parser")
    left_table = soup.find("table",{"class":"left"})
    right_table = soup.find("table",{"class":"right"})
    left_tdtag = left_table.find_all('td')
    right_tdtag = right_table.find_all('td')
    left_text = [None] * int(len(left_tdtag)/2)
    right_text = [None] * int(len(right_tdtag)/2)
    for i in range(0, len(left_text)):
        left_text[i] = left_tdtag[i*2].text
    for i in range(0, len(right_text)):
        right_text[i] = right_tdtag[i*2].text
    return left_text+right_text

def main():
    # Get a list of all possible subject areas
    subject_areas = subject_area_scrape()

    #Use the subject area list to produce lists of all course URLS
    all_urls = subject_area_courses_scrape(subject_areas)
    #top5 = all_urls[:5]
    #top5 = [None, 'https://web.uvic.ca/calendar2019-01/CDs/ENGL/427.html']
    info_dict = {}
    page_scrape(all_urls, info_dict)
    print(info_dict)
    with open('data.json', 'w') as outfile:
        json.dump(info_dict, outfile)

if __name__== "__main__":
  main()
