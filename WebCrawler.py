import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urlparse
from io import StringIO
from html.parser import HTMLParser
import re

### DB-Parameter
DBconfig = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'searchengine',
  'raise_on_warnings': True
}

maxDepth=2

#url = 'https://www.google.de'
# gibt html code der gewünschten url zurück
def get_url_content(url):
    return requests.get(url).text

    
## Sucht alle HREFs auf der Seite und gibt die links als Liste zurück
def getAllLinks(soup):
    links=[]
    
    for a in soup.find_all(href=True):
        links.append(a['href'])
        #print("Found the URL:", a['href'])
    return links

## Sucht alle Bilder auf der Seite und gibt die links als Liste zurück
def getAllImages(soup):
    images=[]
    
    for img in soup.findAll('img'):
        images.append(img.get('src'))
        #print("Found the Image:", img.get('src'))
    return images

## Gibt den Titel der Website zurück
def getTitle(soup):    
    return soup.title.text

## Alle Wörter der Seite zurückgeben
def getAllWords(soup):
    str=soup.text.replace("\n"," ").replace("\xa0"," ")
    words=re.findall("[a-zA-Z0-9äöüÄÖÜß][a-zA-Z0-9äöüÄÖÜß\-\_]*[a-zA-Z0-9äöüÄÖÜß]",str)

    return words




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
    cnx.commit()
    
    cnx.close()

    ### Prüft, ob URL in DB vorhanden ist, wenn ja, returned False
def checkIfShouldCrawl(url):
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    query="""SELECT EXISTS(SELECT id FROM links 
        WHERE link="{}")""".format(url)
    #print(query)
    mycursor.execute(query)
    myresult = mycursor.fetchone()[0]

    cnx.close()
    if myresult==0: return True
    else: return False

def writeAllWords(words,siteId):
    wordData=[]

    for word in words:
        wordData.append((word,startSite[0]))

    ### Crawled den angegebenen Link, die Tiefe dient zur limitierung
def crawlLink(startSite,currentDepth):
    global maxDepth
    startLink=startSite[1]
    print("Now crawling: {}".format(startLink))
    title=""
    allLinks=[]
    allImages=[]
    allWords=[]
    content = get_url_content(startLink)
    
    # übergebe html an beautifulsoup parser
    soup = BeautifulSoup(content, "html.parser")
    
    try:
        allLinks=getAllLinks(soup)
        allImages=getAllImages(soup)
        allWords=getAllWords(soup)
        title=getTitle(soup)
    except:
        print("An error occurred!")

    writeLinkToDB(startLink,title)

    writeAllWords(allWords,startSite[0])
    


    if currentDepth<=maxDepth:

        for link in allLinks:

            ## Format des Link prüfen, wenn ohne hostname-> diesen zufügen
            if link.startswith("/"):

                parsed_uri=urlparse(startLink)
                result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                link=result+link

            else:
                if link.startswith("http"):
                    continue
                parsed_uri=urlparse(startLink)
                result = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=parsed_uri)
                link=result+link
            
            ## Link crawlen
            shouldCrawl=checkIfShouldCrawl(link)
            if shouldCrawl:
                crawlLink(link,currentDepth+1)
             

### MAIN-Code

    
startSite=getStartSite()
if(startSite!=None):
    depth=0
    startURL=startSite[1]
    crawlLink(startSite,0)

           

    
    
else:
    print("Alle Datensätze aktuell, Web wird nicht gecrawled.")



