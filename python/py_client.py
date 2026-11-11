import http.client

connection = http.client.HTTPConnection("192.168.4.1")      # luodaa yhteys, tähä IP
connection.request("GET", "/")                                      # 
response = connection.getresponse()                                 # vastauksena haetaan kuva
print("Status: {} and reason: {}".format(response.status, response.reason)) # status ehkä errorin handlaamisee?
print(response.length)
connection.close()


"""

"""