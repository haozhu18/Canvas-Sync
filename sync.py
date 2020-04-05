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
    '''

    start_time = course.get('start_at', None)
    if start_time != None:
        return start_time.split('T')[0]
    return 'Course not Accessible'


def find_active(course_threshold=3):
    '''
    Get the ids of the active courses the user is enrolled in. Default 3 class
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
    '''

    file_path = path + file
    if pathlib.Path(file_path).exists():
        return True
    # https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them


def request_files(course_id, filepath):
    '''
    Request only files from files section.
    '''

    request_url = request_url_base + course_id + '/files' + request_url_token
    response = requests.get(request_url)
    for file in response.json():
        if not check_exist(filepath, file['filename']):
            print('Downloading: ', file['filename'])
            r = requests.get(file['url'], stream=True)
            with open(filepath + r'\{}'.format(file['filename']), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: 
                        f.write(chunk)


def request_module(course_id, filepath):
    '''
    Request only files from module section.
    '''

    request_url = request_url_base + course_id + '/modules' + request_url_token
    response = requests.get(request_url)
    for module in response.json():
        module_url = module['items_url'] + request_url_token + '&per_page=100'
        new_response = requests.get(module_url)
        list_files = new_response.json()
        for file in list_files:
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


def work():
    '''
    Now get those files
    '''

    courses_info = find_active()
    for name, course_id in courses_info.items():
        filepath = FILEPATH_BASE + r'\{}'.format(name)
        test_request = request_url_base + course_id + '/files' + request_url_token
        test_response = requests.get(test_request)
        if test_response.json() != [] and test_response.status_code != 401:
            request_files(course_id, filepath)
        else:
            request_module(course_id, filepath)