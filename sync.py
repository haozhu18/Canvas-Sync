import requests
import pathlib
import re


TOKEN = open('token.txt').read()
request_url_base = 'https://canvas.uchicago.edu/api/v1/courses/'
request_url_token = '?access_token=' + TOKEN

FILEPATH_BASE = r'C:\Users\Razer\Documents'


def sort_helper(course):
    '''
    When sorting, disregard courses that are not accessible bc of date

    Input: course: (str) name of a course

    Output: The start time of the course or 'Course not Accessible'
    '''

    start_time = course.get('start_at', None)
    if start_time != None:
        return start_time.split('T')[0]
    return 'Course not Accessible'


def find_active(course_threshold=3):
    '''
    Get the ids of the active courses the user is enrolled in. Default 3 class

    Input: course_thershold: (int) the number of courses to find information

    Output: A dictionary with key course name and value course id 
    '''

    # is sorting not built in?
    course_dict = {}
    num_courses = 0
    course_url = request_url_base + request_url_token + '&per_page=100'
    list_courses = requests.get(course_url).json()
    sorted_courses = sorted(list_courses, key=sort_helper, reverse=True)
    for course in sorted_courses:
        if num_courses == course_threshold:
            break
        if 'start_at' in course:
            course_name = re.findall(r'(\w+\s*\w+)\s', course['name'])[0]
            course_dict[course_name] = str(course['id'])
            num_courses += 1
    return course_dict

    # problem: how to determine the default number of classes?


def check_exist(path, file):
    '''
    Check if the file exists in our directory by comparing name

    Inputs:
        path: a certain path to a directory
        file: the name of a certain file

    Output: True or False
    '''

    file_path = path + r'\{}'.format(file)
    return pathlib.Path(file_path).exists()
    # https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them


def request_files(course_id, filepath):
    '''
    Request only files from files section.

    Inputs:
        course_id: (str) the id of a course in the canvas system
        filepath: a certain path to a directory
    '''

    request_url = request_url_base + course_id + '/files' + \
                  request_url_token + '&per_page=100'
    response = requests.get(request_url)
    for file in response.json():
        # if the file is an url to an external website for example, skip
        if file.get('type', 'notFile') != 'File':
            continue
        if not check_exist(filepath, file['filename']):
            print('Downloading: ', file['filename'])
            r = requests.get(file['url'], stream=True)
            with open(filepath + r'\{}'.format(file['filename']), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: 
                        f.write(chunk)
        else:
            print('!', file['display_name'], 'already exists')


def request_module(course_id, filepath):
    '''
    Request only files from module section.

     Inputs:
        course_id: (str) the id of a course in the canvas system
        filepath: a certain path to a directory
    '''

    request_url = request_url_base + course_id + '/modules' + \
                  request_url_token + '&per_page=100'
    response = requests.get(request_url)
    for module in response.json():
        module_url = module['items_url'] + request_url_token + '&per_page=100'
        new_response = requests.get(module_url)
        list_files = new_response.json()
        for file in list_files:
            # if the file is an url to an external website for example, skip
            if file.get('type', 'notFile') != 'File':
                continue
            file_url = file['url'] + request_url_token 
            file_response = requests.get(file_url)
            file = file_response.json()
            if not check_exist(filepath, file['display_name']):
                print('Downloading: ', file['display_name'])
                r = requests.get(file['url'], stream=True)
                with open(filepath + r'\{}'.format(file['display_name']), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: 
                            f.write(chunk)
            else:
                print('!', file['display_name'], 'already exists')


def work():
    '''
    Download files of interest from canvas
    '''

    courses_info = find_active()
    for name, course_id in courses_info.items():
        filepath = FILEPATH_BASE + r'\{}'.format(name)
        # a test request to see whether the files are in the files section or
        # the modules section
        test_request = request_url_base + course_id + '/files' + request_url_token
        test_response = requests.get(test_request)
        if test_response.json() != [] and test_response.status_code != 401:
            request_files(course_id, filepath)
        else:
            # observation: even if the class has no module or files, running
            # this code does not give an error.
            request_module(course_id, filepath)

# idea: if newly uploaded files are at the end of the module/ file section
#       a way to improve speed is to let the program remember the pagigation
#       of where it ended and start from there in the next request