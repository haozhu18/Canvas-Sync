import requests
from os import listdir
from os.path import isfile, join

MATH = r'C:\Users\Razer\Documents\MATH 19620'
ECON = r'C:\Users\Razer\Documents\ECON 20110'
KORE = r'C:\Users\Razer\Documents\KORE 102'
math_files = [f for f in listdir(MATH) if isfile(join(MATH, f))]
econ_files = [f for f in listdir(ECON) if isfile(join(ECON, f))]
kore_files = [f for f in listdir(KORE) if isfile(join(KORE, f))]

# improve the id lookup part by using regular expressions
math_id = '23490000000026278'
econ_id = '23490000000026084'
kore_id = '23490000000025976'

TOKEN = '2349~NJdRVMVkzSi9Dum0eDUFPxeszy0WMPNye38gRhggs03OH1NteKm7ilYA1yQROLW0'
request_url_base = 'https://canvas.uchicago.edu/api/v1/courses/'
request_url_token = '?access_token=' + TOKEN

math_request_url = request_url_base + math_id + '/files' + request_url_token
econ_request_url = request_url_base + econ_id + '/modules' + request_url_token
kore_request_url = request_url_base + kore_id + '/modules' + request_url_token

math_response = requests.get(math_request_url)
econ_response = requests.get(econ_request_url)
kore_response = requests.get(kore_request_url)

for file in math_response.json():
    # improve this by comparing file content, enabling custom file names
    if file['filename'] not in math_files:
        print('Downloading: ', file['filename'])
        r = requests.get(file['url'], stream=True)
        with open(MATH + r'\{}'.format(file['filename']), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: 
                    f.write(chunk)

for module in econ_response.json():
    module_url = module['items_url'] + request_url_token + '&per_page=100'
    new_response = requests.get(module_url)
    list_files = new_response.json()
    for file in list_files:
        file_url = file['url'] + request_url_token 
        file_response = requests.get(file_url)
        file = file_response.json()
        if file['display_name'] not in econ_files:
            print('Downloading: ', file['display_name'])
            r = requests.get(file['url'], stream=True)
            with open(ECON + r'\{}'.format(file['display_name']), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: 
                        f.write(chunk) 

for module in kore_response.json():
    module_url = module['items_url'] + request_url_token + '&per_page=100'
    new_response = requests.get(module_url)
    list_files = new_response.json()
    for file in list_files:
        file_url = file['url'] + request_url_token 
        file_response = requests.get(file_url)
        file = file_response.json()
        if file['display_name'] not in kore_files:
            print('Downloading: ', file['display_name'])
            r = requests.get(file['url'], stream=True)
            with open(KORE + r'\{}'.format(file['display_name']), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: 
                        f.write(chunk)