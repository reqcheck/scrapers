import webbrowser
import requests
from bs4 import BeautifulSoup
import csv
import re
import json

def page_scrape(all_urls, info_dict):
    for url in all_urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        course_dict = {}
        course_dict['units'] = None
        course_dict['hours'] = None
        course_dict['pre_reqs'] = None
        course_dict['co_reqs'] = None
        course_dict['subject'] = None
        course_dict['name'] = None
        course_dict['url'] = url

        h4s = soup.find('h4')
        subject = re.findall("[A-Z]{2,4}\s\d\d\d\w?", h4s.text)
        course_dict['subject'] = subject[0]
        name = re.findall("[A-Z]{2,4}\s\d\d\d\w?\s(.*)", h4s.text)
        course_dict['name'] = name[0]

        pees = soup.find_all('p')
        for p in pees:
            if re.match(r'Credits:.*', p.text):
                course_dict['units'] = re.findall(r'([0-9]{1}\w?)',p.text)[0]
            if re.match(r'Pre-reqs:.*', p.text):
                allOf = re.findall(r'[A|a]ll of (.*)', p.text)
                oneOf = re.findall(r'[O|o]ne of (.*)?(?:;|and)', p.text)
                print(allOf)
                print(oneOf)
                allOfList = None
                oneOfList = None
                if len(allOf) > 0:
                    allOfList = re.findall(r'([a-zA-Z]{2,4}\s[0-9]{3}\w?)',allOf[0])
                if len(oneOf) > 0:
                    oneOfList = re.findall(r'([a-zA-Z]{2,4}\s[0-9]{3}\w?)',oneOf[0])

                if allOfList is None and oneOfList is None:
                    course_dict['pre_reqs'] = None
                elif allOfList is None:
                    course_dict['pre_reqs'] = [oneOfList]
                elif oneOfList is None:
                    course_dict['pre_reqs'] = allOfList
                else:
                    course_dict['pre_reqs'] = allOfList + [oneOfList]

            if re.match(r'Co-reqs:.*', p.text):
                allOf = re.findall(r'[A|a]ll of (.*)', p.text)
                oneOf = re.findall(r'[O|o]ne of of (.*)', p.text)
                allOfList = None
                oneOfList = None
                if len(allOf) > 0:
                    allOfList = re.findall(r'([a-zA-Z]{2,4}\s[0-9]{3}\w?)',allOf[0])
                if len(oneOf) > 0:
                    oneOfList = re.findall(r'([a-zA-Z]{2,4}\s[0-9]{3}\w?)',oneOf[0])

                if allOfList is None and oneOfList is None:
                    course_dict['co_reqs'] = None
                elif allOfList is None:
                    course_dict['co_reqs'] = oneOfList
                elif oneOfList is None:
                    course_dict['co_reqs'] = allOfList
                else:
                    course_dict['co_reqs'] = allOfList + oneOfList

        table = soup.find('table', {'class': 'table table-striped section-summary'})
        rows = table.find_all('tr')

        print(course_dict)
        info_dict[course_dict['subject']] = course_dict

def subject_areas_courses_scrape(subject_areas):
    all_urls = ['None']
    for area in subject_areas:
        url = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-department&dept=" + area
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        for trtag in soup.find_all('tr',{"class":"section1"}):
            course = trtag.find('a').text
            course_num = re.search(r'([0-9]{3}\w?)', course)
            #print("\n")
            #print(course_num.group())
            all_urls.append('https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept='+area+'&course='+course_num.group())

    del all_urls[0]
    print(all_urls)
    return all_urls


def subject_area_scrape():
    page = requests.get('https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-all-departments')
    soup = BeautifulSoup(page.text, "html.parser")
    maintable = soup.find("table",{"id":"mainTable"})
    areas = ['None']
    for a in maintable.find_all("a"):
        areas.append(a.text)
    del areas[0]
    return areas

def main():
    #subject_areas = subject_area_scrape()
    #all_urls = subject_areas_courses_scrape(subject_areas)
    all_urls = ['https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept=BIOC&course=460']
    info_dict = {}
    page_scrape(all_urls, info_dict)

if __name__== "__main__":
  main()
