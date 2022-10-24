# -*- coding: utf-8 -*-
"""sitemap_url_indexing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YJHVdJBsyq2Xwsix4TCXTiaFw6meNAIw
"""

#Task per migliorare il codice:
#FATTO - Check se gli url della sitemap sono in 200
#storage in un db light tutti gli url
#sottrazione degli url nel db meno quelli nuovi trovati e push dei soli nuovi
from oauth2client.transport import request
!pip install oauth2client httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build 
from googleapiclient.http import BatchHttpRequest
import httplib2
import json
import urllib.request
import requests
from bs4 import BeautifulSoup
from datetime import date

#Recupera gli url di una sitmeap e li trasforma in array
sitemap = requests.get("https://example.it/sitemap.xml")

payload = BeautifulSoup(sitemap.content, "xml")

urls_from_xml = []

#Cattura tutti i loc anche image:loc
#loc_tags = payload.find_all('loc')

#Cattura solo i loc principali <loc>
loc_tags = [el for el in payload.find_all('loc') if not el.prefix]

for loc in loc_tags:
    urls_from_xml.append(loc.get_text())

#Scarta gli url non in 200
url_status_ok = []
for sitemapurl in urls_from_xml:
  request_response = requests.head(sitemapurl)
  status_code = request_response.status_code
  if status_code == 200:
    url_status_ok.append(sitemapurl)


#Crea un file txt con gli URL
dt = str(date.today().isoformat())
file_data = "sitemap-url-"+dt+".txt"
db = open(file_data, "w+")
for listitem in url_status_ok:
    db.write(f'{listitem}\n')
db.close()


#Crea un JSON con la coppia URL 
#Cambiando URL_UPDATED in URL_DELETED si possono rimuovere gli URL
raw_data = ""
k = 0 #imposto var a zero

for itemurl in url_status_ok:

  raw_data += '"'+itemurl+'" : "URL_UPDATED",'

  k += 1 #aumento di 1

  if k == 100: #ogni 10 faccio cose

    clean_data = "{"+raw_data.rstrip(',')+"}"

    json_request = json.loads(clean_data)

    #print(json_request)

    #Chiamata API alle indexing api
    requests = json_request
    
    #Percorso del file delle credenziali (root) da caricare su Colab
    JSON_KEY_FILE = "credentials.json"
    
    SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    
    #Autorizzazione credenziali
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    
    #Creazione del servizio
    service = build('indexing', 'v3', credentials=credentials)
    
    def insert_event(request_id, response, exception):
        if exception is not None:
          print(exception)
        else:
          print(response)
    
    batch = service.new_batch_http_request(callback=insert_event)
    
    for url, api_type in requests.items():
        batch.add(service.urlNotifications().publish(
            body={"url": url, "type": api_type}))
    
    batch.execute()
    
    raw_data = "" #svuoto

    k = 0 # svuoto

if k < 100:
  clean_data = "{"+raw_data.rstrip(',')+"}"

  json_request = json.loads(clean_data)
  
  requests = json_request

  JSON_KEY_FILE = "credentials.json"
  
  SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
  ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
  
  credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
  http = credentials.authorize(httplib2.Http())
  
  service = build('indexing', 'v3', credentials=credentials)
  
  def insert_event(request_id, response, exception):
      if exception is not None:
        print(exception)
      else:
        print(response)
  
  batch = service.new_batch_http_request(callback=insert_event)
  
  for url, api_type in requests.items():
      batch.add(service.urlNotifications().publish(
          body={"url": url, "type": api_type}))
  
  batch.execute()