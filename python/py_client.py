import http.client
import cv2 as cv
import numpy as np

import imgproc_test as ip

connection = http.client.HTTPConnection("10.61.14.225")      # luodaa yhteys, tähä IP
connection.request("GET", "/")                                      # 
response = connection.getresponse()                                 # vastauksena haetaan kuva
print("Status: {} and reason: {}".format(response.status, response.reason)) # status ehkä errorin handlaamisee?
print(response.length)
print(type(response))

print("header:")
res_header = response.getheaders()
print(res_header)

# process response data
res_data = response.read()
img = np.asarray(bytearray(res_data),dtype="uint8")
img = cv.imdecode(img, cv.IMREAD_COLOR_RGB)
img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)

connection.close()

print(type(img),np.shape(img))
cv.imshow("image",img)
ip.img_proc(img)