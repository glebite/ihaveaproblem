'''camfinder.py
'''
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import requests
from requests.models import Response
import re
import sys
import logging
import getopt


logging.basicConfig(format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s", filename='camfinder.log',level=logging.DEBUG)


NEXT = '»'

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
    'asp/video.cgi'
    ]


# Supply something for the server to not choke on
headers = {'User-Agent':
           'Mozilla/5.0 (Windows NT 6.1; WOW64)'
           ' AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/56.0.2924.76 Safari/537.36'}


global results
results = list()


def update_camera_url(replace, image, counter):
    '''update_camera_url
    '''
    source_url = image['src']
    logging.info(f'update_camera_url: {source_url=}')
    if replace:
        source_url = re.sub(f'{replace}(\d+)',
                            f'{replace}{counter}', source_url)
    else:
        source_url = image['src']
    logging.info(f'update: {source_url=}')
    return source_url


def find_multi_cam(image):
    '''This function returns the first channel
       number if the image['src'] contains chn= or channel=

       If the channel= appears, then the base counter is 1
       otherwise it's 0 if chn=
    '''
    base = 0
    replace = None
    logging.info(f"image data: {image['src']=}")
    if 'channel=' in image['src']:
        base = 1
        replace = "channel="
    if 'chn=' in image['src']:
        replace = "chn="
        
    return base, replace

def get_image(image_tuple):
    '''This is the beans and rice of the functions.
    '''
    global results

    # logging.info(f'{image_tuple=}')
    image, page, counter = image_tuple
    base, replace = find_multi_cam(image)
    
    logging.info(f'{base=} {replace=}')
    for i in range(base, base+1):
        s = update_camera_url(replace, image, i)
        # address = re.findall(r'(d{1,3}\.d{1,3}\.d{1,3}\.d{1,3})', replace)
        # logging.info(f'Updated information {page=} {i=} {address=}')
        last_img = Response()
        last_img._content = None
        try:
            img = requests.get(s, headers=headers, timeout=10)
            if img.content != last_img.content:
                last_img._content = img.content
                file_name = f'{page}-{base}-{counter}-remote.jpg'
                with open(file_name, 'wb') as f:
                    f.write(img.content)
                logging.info(f'Appending: {file_name=}')
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
        logging.debug(f'{type(results)}')
        for (image_filename, s, image) in results:
            logging.info(f'Updating html page with {image_filename=}')
            fp.write(f'<br/><img src="./{image_filename}"'
                     ' width="800" height="600" ></img>')
            fp.write(f'<br/>{s}<br/>{image["src"]}<br/> {image["title"]}')
        fp.write('</body></html')
    logging.info('Finished writing output')


def main(country=None, city=None, interest=None):
    '''
    Allows for searching one one of the things we want to look for

    bycountry example IR, CA, FR, TW
    mapcity Isfahan, Toronto
    bytag Restaurant, Bar, Gym, Office
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
    page = 1
    executor = ThreadPoolExecutor(5)

    futures = list()
    while True:
        if page > 1:
            URL = f'http://www.insecam.org/en/{tag}/{criteria}/?page={page}'
        else:
            URL = f'http://www.insecam.org/en/{tag}/{criteria}'
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
                continue
            futures.append(executor.submit(get_image, (image, page, counter)))
            
        wait(futures)                  
        nextp = re.search(f'page={page+1}', str(page_data.content))
        if nextp:
            page += 1
        else:
            break
    results = list(dict.fromkeys(results))
    output_html(results)

def help():
    print("python camfinder.py [-c country | -C city | -i interest]")

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:C:i:", ["help", "output="])
    except getopt.GetoptError as err:
        help()
        logging.error(err)
        sys.exit(2)
    for o, a in opts:
        if o in ("-c"):
            main(country=a)
            break
        elif o in ("-C"):
            main(city=a)
            break
        elif o in ("-i"):
            main(interest=a)
            break
    else:
        help()
