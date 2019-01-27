import webbrowser
import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import math
import time


class RateMyProfScraper:
        def __init__(self,schoolid):
            self.UniversityId = schoolid
            self.professorlist = self.createprofessorlist()
            self.indexnumber = False

        def createprofessorlist(self):#creates List object that include basic information on all Professors from the IDed University
            tempprofessorlist = []
            num_of_prof = self.GetNumOfProfessors(self.UniversityId)
            num_of_pages = math.ceil(num_of_prof / 20)
            i = 1
            while (i <= num_of_pages):# the loop insert all professor into list
                page = requests.get("http://www.ratemyprofessors.com/filter/professor/?&page=" + str(
                    i) + "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                    self.UniversityId))
                temp_jsonpage = json.loads(page.content)
                temp_list = temp_jsonpage['professors']
                tempprofessorlist.extend(temp_list)
                i += 1
            return tempprofessorlist

        def GetNumOfProfessors(self,id):  # function returns the number of professors in the university of the given ID.
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                    id))  # get request for page
            temp_jsonpage = json.loads(page.content)
            num_of_prof = temp_jsonpage[
                              'remaining'] + 20  # get the number of professors at William Paterson University
            return num_of_prof

        def SearchProfessor(self, ProfessorName):
            self.indexnumber = self.GetProfessorIndex(ProfessorName)
            if self.indexnumber == False:
                return "error"
            else:
                return self.professorlist[self.indexnumber]['overall_rating']
            return self.indexnumber

        def GetProfessorIndex(self,ProfessorName):  # function searches for professor in list
            for i in range(0, len(self.professorlist)):
                if (ProfessorName == (self.professorlist[i]['tFname'] + " " + self.professorlist[i]['tLname'])):
                    return i
            return False  # Return False is not found



def prof_list(all_courses, prof_dict, RMP_dict):
    for course in all_courses:
        print("\n\nNew Course:" + course[0] + course[1])
        summer_url = "https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in=201905&subj_in="+course[0]+"&crse_in="+course[1]+"&schd_in="
        fall_url = "https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in=201809&subj_in="+course[0]+"&crse_in="+course[1]+"&schd_in="
        spring_url = "https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse?term_in=201901&subj_in="+course[0]+"&crse_in="+course[1]+"&schd_in="
        summer_page = requests.get(summer_url)
        fall_page = requests.get(fall_url)
        spring_page = requests.get(spring_url)
        summer_soup = BeautifulSoup(summer_page.text, "html.parser")
        fall_soup = BeautifulSoup(fall_page.text, "html.parser")
        spring_soup = BeautifulSoup(spring_page.text, "html.parser")
        names = [re.findall(r'(.*)\(P\)', summer_soup.text)]
        names.append(re.findall(r'(.*)\(P\)', fall_soup.text))
        names.append(re.findall(r'(.*)\(P\)', spring_soup.text))
        names_final = [x for x in names if x != []]
        course_code = str(course[0]) + ' ' + str(course[1])
        flat_list = [item.rstrip() for sublist in names_final for item in sublist]
        flatter_list = list(set([" ".join(string.split()) for sublist in names_final for string in sublist]))
        course_list = ['None']
        for prof in flatter_list:
            if prof in RMP_dict:
                rating = RMP_dict[prof]
            else:
                rating = None
            prof_list = [prof, rating]
            course_list.append(prof_list)
        del course_list[0]
        prof_dict[course_code] = course_list
    return prof_dict




def subject_area_courses_scrape(subject_areas):
    #open the area page
    all_courses = [None]
    for area in subject_areas:
        url = "https://web.uvic.ca/calendar2019-01/CDs/"+area+"/CTs.html"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        tdtag = soup.find_all('td')
        for i in range(0, int(len(tdtag)/2)):
            all_courses.append([area,tdtag[i*2].text])
    return all_courses


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
    print("here 1")

    #Use the subject area list to produce lists of all course URLS
    all_courses = subject_area_courses_scrape(subject_areas)
    del all_courses[0]
    print("here 2")

    uvic = RateMyProfScraper(1488)
    RMP_dict= {}
    for prof in uvic.professorlist:
        name = prof['tFname'] + ' ' + prof['tLname']
        if prof['overall_rating'] == 'N/A':
            RMP_dict[name] = None
        else:
            RMP_dict[name] = prof['overall_rating']

    print("here 3")
    prof_dict = {}
    prof_list(all_courses, prof_dict, RMP_dict)
    print("here 4")

    with open('RMPData.json', 'w') as outfile:
        json.dump(prof_dict, outfile)

if __name__== "__main__":
    main()
