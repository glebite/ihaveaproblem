"""
Code lifted from:
https://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera
"""
import cv2
import requests
import numpy as np


# URL = 'http://185.72.27.244:85/mjpg/video.mjpg'
URL = 'http://37.221.17.136:9000/cgi-bin/faststream.jpg?stream=half&fps=15&rand=COUNTER'


r = requests.get(URL, stream=True)
if(r.status_code == 200):
    bytes = bytes()
    for chunk in r.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('i', i)
            if cv2.waitKey(1) == 27:
                exit(0)
else:
    print("Received unexpected status code {}".format(r.status_code))
