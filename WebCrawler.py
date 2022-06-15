import requests
from bs4 import BeautifulSoup
import mysql.connector

### DB-Parameter
DBconfig = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'searchengine',
  'raise_on_warnings': True
}


#url = 'https://www.google.de'
# gibt html code der gewünschten url zurück
def get_url_content(url):
    return requests.get(url).text

    
## Sucht alle HREFs auf der Seite und gibt die links als Liste zurück
def getAllLinks(url):
    links=[]
    content = get_url_content(url)
    # übergebe html an beautifulsoup parser
    soup = BeautifulSoup(content, "html.parser")
    
    for a in soup.find_all(href=True):
        links.append(a['href'])
        #print("Found the URL:", a['href'])
    return links

## Sucht alle Bilder auf der Seite und gibt die links als Liste zurück
def getAllImages(url):
    images=[]
    content = get_url_content(url)
    # übergebe html an beautifulsoup parser
    soup = BeautifulSoup(content, "html.parser")
    
    for img in soup.findAll('img'):
        images.append(img.get('src'))
        #print("Found the Image:", img.get('src'))
    return images

## Gibt den Titel der Website zurück
def getTitle(url):
    content = get_url_content(url)
    # übergebe html an beautifulsoup parser
    soup = BeautifulSoup(content, "html.parser")
    
    return soup.title.text

## Holt Seite von der DB, welche am längsten nicht gecrawled wurde
def getStartSite():
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    mycursor.execute("""SELECT *
                FROM links
                WHERE timestamp_visited <= DATE_SUB(NOW(), INTERVAL 1 DAY)
                ORDER BY timestamp_visited DESC
                LIMIT 1 """)

    myresult = mycursor.fetchone()
    
    cnx.close()
    return myresult

def writeLinkToDB(url, title):
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    query="""INSERT INTO links(link, title, timestamp_visited)
                    VALUES( "{}", "{}",NOW())
                    ON DUPLICATE KEY
                    UPDATE title = "{}", timestamp_visited = NOW();""".format(url, title,title)
    #print(query)
    mycursor.execute(query)
                
    
    cnx.close()



### MAIN-Code

maxDepth=3
    
startSite=getStartSite()
if(startSite!=None):
    depth=0
    startURL=startSite[1]
    print("Now crawling: {}".format(startURL))
    title=getTitle(startURL)
    allLinks=getAllLinks(startURL)
    allImages=getAllImages(startURL)

    writeLinkToDB(startURL,title)

    for link in allLinks:
        if depth<=maxDepth:
            

    
    
else:
    print("Alle Datensätze aktuell, Web wird nicht gecrawled.")



