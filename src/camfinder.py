'''
camfinder.py

Magic tool.
'''
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import requests
from requests.models import Response
import re
import sys
import logging
from logging import config
import getopt
import argparse
import cv2
import numpy as np


config.fileConfig("logger.conf")
logger = logging.getLogger("root")


NEXT = '»'
BASE_URL = 'http://www.insecam.org/en'


'''
These are stream sources that "stream" instead of providing
a single image.  Until there is fix for that to retrieve just
a static image, the code will "continue"

OpenCV might be employed here.
'''
PROBLEMATIC_STREAM_SOURCES = [
    'mjpg',
    'mjpeg',
    'videostream',
    'GetOneShot',
    'action=stream',
    'GetData',
    'cam_1.cgi',
    'faststream',
    'asp/video.cgi',
    'speed='
    ]


# Supply something for the server to not choke on
headers = {'User-Agent':
           'Mozilla/5.0 (Windows NT 6.1; WOW64)'
           ' AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/56.0.2924.76 Safari/537.36'}


global results
global problems
results = list()
problems = list()
data_store = False


def video_capture_image(URL, image_name):
    """extract a video still from a stream

    Parameters:
    URL        (str): the URL for the camera retrieval
    image_name (str): the name to save/retrieve the image

    Returns:
    n/a
    """
    result = requests.get(URL, stream=True)
    if(result.status_code == 200):
        data = bytes()
        for chunk in result.iter_content(chunk_size=1024):
            data += chunk
            a = data.find(b'\xff\xd8')
            b = data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = data[a:b+2]
                data = data[b+2:]
                image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                cv2.imwrite(image_name, image)
                break
    else:
        logging.error(f"Received unexpected status code {result.status_code}")


def update_camera_url(replace, image, counter):
    '''
    update_camera_url

    Parameters:
    replace 
    image
    counter
    
    Returns:
    source_url
    '''
    source_url = image['src']
    logging.info(f'{source_url=}')
    if replace:
        source_url = re.sub(f'{replace}(\d+)',
                            f'{replace}{counter}', source_url)
    else:
        source_url = image['src']
    logging.info(f'leaving {source_url=}')
    return source_url


def write_out_url(url):
    with open('datastore.txt', 'a') as fp:
        fp.write(url + '\n')


def find_multi_cam(image):
    '''This function returns the first channel
       number if the image['src'] contains chn= or channel=

       If the channel= appears, then the base counter is 1
       otherwise it's 0 if chn=
    '''
    logging.debug(f'{image}')
    base = 0
    replace = None
    logging.debug(f"image data: {image['src']=}")
    if 'channel=' in image['src']:
        logging.debug(f"Checking for 'channel='")
        base = 1
        replace = "channel="
    if 'chn=' in image['src']:
        logging.debug(f"Checking for 'chn='")
        replace = "chn="
    logging.debug(f'leaving {base=} {replace=}')
    return base, replace


def get_image(image_tuple):
    '''This is the beans and rice of the functions.

    Parameters:
    image_tuple ()

    Returns:
    n/a

    '''
    global results

    # logging.info(f'{image_tuple=}')
    image, page, counter = image_tuple
    base, replace = find_multi_cam(image)
    
    logging.info(f'Setting up the base and replacement: {base=} {replace=}')

    if data_store:
        write_out_url(image['src'])

    last_img = Response()
    last_img._content = None    
    for i in range(base, base+32):
        s = update_camera_url(replace, image, i)

        address = re.search(r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)', image['src']).group(0)
        logging.info(f'Updated information {page=} {i=} {address=}')

        try:
            img = requests.get(s, headers=headers, timeout=20)
            logging.debug(f'Status: {img.status_code=}')
            logging.debug(f'Sorting out things: {address=}, {s=}')
            if img.content != last_img.content:
                last_img._content = img.content
                file_name = f'{page}-{base}-{i}-{address}.jpg'
                with open(file_name, 'wb') as f:
                    f.write(img.content)
                logging.info(f'About to append: {file_name=} {s=} {image=}')
                results.append((file_name, s, image))
            else:
                break
        except Exception as e:
            logging.error(f'Exception: {e} {i=} {s=}')
            break
        if not replace:
            break


def output_html(results):
    '''output_html - dump the contents of "results"
    '''
    logging.info(f'Coming into output_html with {results=}')
    with open('index.html', 'w') as fp:
        fp.write('<html><body>')
        fp.write('<h1>Static image links</h1>')
        fp.write('<br/>Clicked links will open in a new tab<br/>')
        logging.debug(f'{type(results)}')
        for (image_filename, s, image) in results:
            logging.debug(f'Updating html page with {image_filename=}')
            fp.write(f'<br/><img src="./{image_filename}"'
                     ' width="800" height="600" ></img>')
            fp.write(f'<br/><a href="{s}" target="_blank" rel="nopener no referrer">{s}</a><br/> {image["title"]}')
        fp.write('<h1>Streamed image links</h1>')
        fp.write('<br/>Clicked links will open in a new tab<br/>')        
        for image in problems:
            s = image['src']
            t = image['title']
            video_capture_image(s, f'{t}.jpg')
            fp.write(f'<br/><img src="./{t}.jpg" width="800" height="600"></img>')            
            fp.write(f'<br/>Streaming: <a href="{s}" target="_blank" rel="nopener no referrer">{s}</a><br/> {t}')
        fp.write('</body></html')
    logging.info('Finished writing output')


def main(country=None, city=None, interest=None):
    '''
    Allows for searching one one of the things we want to look for

    bycountry example IR, CA, FR, TW
    mapcity Isfahan, Toronto
    bytag Restaurant, Bar, Gym, Office

    Parameters:
    country  (str): country code (defaults to None)
    city     (str): city name (defaults to None)
    interest (str): interest name (defaults to None)
    '''
    if country:
        tag = 'bycountry'
        criteria = country
    elif city:
        tag = 'bycity'
        criteria = city
    elif interest:
        tag = 'bytag'
        criteria = interest
    else:
        pass
    logging.info(f'Starting acquisition of images: {country=}'
                 f' {city=} {interest=}')
    global results
    global problems
    page = 1
    executor = ThreadPoolExecutor(10)

    futures = list()
    while True:
        if page > 1:
            URL = f'{BASE_URL}/{tag}/{criteria}/?page={page}'
        else:
            URL = f'{BASE_URL}/{tag}/{criteria}'
        logging.info(f'{URL=}')
        page_data= requests.get(URL, headers=headers)

        soup = BeautifulSoup(page_data.content, 'html.parser')

        images = soup.find_all("img",
                               {"class":
                                "thumbnail-item__img img-responsive"})

        logging.info(f'Checking images: {images=}')
        for counter, image in enumerate(images):
            if re.compile('|'.join(PROBLEMATIC_STREAM_SOURCES),
                          re.IGNORECASE).search(image['src']):
                # add the image src to list of unsupported formats
                problems.append(image)
                continue
            # get_image((image, page, counter))
            futures.append(executor.submit(get_image, (image, page, counter)))
            
        wait(futures)                  
        nextp = re.search(f'page={page+1}', str(page_data.content))
        if nextp:
            logging.debug(f'Next page: {page=}')
            page += 1
        else:
            break
    results = list(dict.fromkeys(results))
    results = sorted(results, key=lambda tup: tup[1])
    output_html(results)


def list_countries():
    """ REST API call and retrieves a json list of 
        countries, names, and count of cameras there.
    """
    response = requests.get(f'{BASE_URL}/jsoncountries', headers=headers)
    data = response.json()
    for country in data['countries']:
        name, count = data['countries'][country].items()
        print(f'{country:<2s} {name[1]:.<40s} {count[1]}')

        
def list_cities():
    """ Sigh - why they didn't use a REST API for this, I have
        no idea at all.  The page must be retrieved and then
        parsed via beautiful soup.
     
        One city has two forward slashes and that is handled by
        counting the number of slashes and deviating for things
        here.
    """
    response = requests.get(f'{BASE_URL}/mapcity', headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all("a", href=lambda href: href and "bycity" in href)
    for link in links:
        results = link.text.split('/')
        if len(results) == 3:
            city, _, count = results
        else:
            city, count = results
        count = count.lstrip()[1:-1]
        print(f'{city:,<50s} {count}')


def list_interests():
    """ REST API call and retrieves a json list of 
        interests (tags).
    """
    response = requests.get(f'{BASE_URL}/jsontags', headers=headers)
    data = response.json()
    for tag in data['tags']:
        name = data['tags'][tag]
        print(name)

    
def help():
    print("python camfinder.py [-I | -L | -l | -c country | -C city | -i interest]")
    print("-c <country> - finds all cameras in the country (uses 2 character country code (except for -)")
    print("-C <city> - all cameras by city name.  Encapsulate names that have spaces in them with quotes")
    print("-i <interest> - lists all interests (tags) such as Restaurant.")
    print("-I - lists interests or tags such as Restaurant")
    print("-L - list of cities")
    print("-l - list of country codes, country names, and number of cameras there.")
    print("-d - dump URLs to a text file")


# def main():
#     """
#     """
#     my_parser = argparse.ArgumentParser()
#     my_parser.add_argument('-c', action='store')
#     my_parser.add_argument('-C', action='store')
#     my_parser.add_argument('-i', action='store')
#     my_parser.add_argument('-l', action='store')
#     my_parser.add_argument('-L', action='store')
#     my_parser.add_argument('-I', action='store')
#     my_parser.add_argument('-d', action='store')


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdlILc:C:i:", ["help", "output="])
    except getopt.GetoptError as err:
        help()
        logging.error(err)
        sys.exit(2)
    for o, a in opts:
        if o in ('-d'):
            data_store = True
        elif o in ("-c"):
            main(country=a)
            break
        elif o in ("-C"):
            main(city=a)
            break
        elif o in ("-i"):
            main(interest=a)
            break
        elif o in ("-l"):
            list_countries()
            break
        elif o in ("-L"):
            list_cities()
            break
        elif o in ("-I"):
            list_interests()
            break
    else:
        help()
