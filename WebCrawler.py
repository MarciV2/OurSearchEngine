import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urlparse
from io import StringIO
from html.parser import HTMLParser
import re
import validators

### DB-Parameter
DBconfig = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'searchengine',
  'raise_on_warnings': True
}

maxDepth=2

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

## Alle Wörter der Seite zurückgeben, anhand von RegEx, wird jedoch nicht gefiltert!!!
def getAllWords(soup):
    str=soup.text.replace("\n"," ").replace("\xa0"," ")
    words=re.findall("[a-zA-Z0-9äöüÄÖÜß][a-zA-Z0-9äöüÄÖÜß\-\_]*[a-zA-Z0-9äöüÄÖÜß]",str)

    return words

## Alternative Methode um Wörter der Seite zu finden
def getAllWords2(soup):
    wordset={""}
    for each_text in soup.findAll("p"):
        if each_text is not None: 
            words=[]
            content = each_text.text
            words = content.lower().split()

            for word in words:
                if validators.url(word):
                    words.remove(word)

       
            wordset.update(words)

    #Stoppwörter löschen (mit Messung&Ausgabe der Anzahl)
    len1=len(wordset)
    wordset=wordset-set(stopwords)
    len2=len1-len(wordset)
    print("removed {} stopwords".format(len2))

    return clean_wordlist(list(wordset))



## Reinigt die Liste von Sonderzeichen
def clean_wordlist(wordlist):
    clean_list = []
    for word in wordlist:
        symbols = "!@#$%^&*()_+={[}]|\;:\"<>?/., '\"©"
        for i in range(len(symbols)):
            word = word.replace(symbols[i], "")
        if len(word) > 0:
            clean_list.append(word)
    return clean_list


## Holt Seite von der DB, welche am längsten nicht gecrawled wurde
def getStartSite():
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    mycursor.execute("""SELECT *
                FROM links
                WHERE timestamp_visited <= DATE_SUB(NOW(), INTERVAL 1 DAY)
                ORDER BY timestamp_visited ASC
                LIMIT 1 """)

    myresult = mycursor.fetchone()
    
    cnx.close()
    return myresult


## Schreibt den Link mit Titel und aktuellem Zeitpunkt auf die DB, gibt die ID zurück
def writeLinkToDB(url, title):
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    queryInsLink="""INSERT INTO links(link, title, timestamp_visited)
                    VALUES( "{}", "{}",NOW())
                    ON DUPLICATE KEY
                    UPDATE title = "{}", timestamp_visited = NOW();""".format(url, title,title)
    queryGetId="""SELECT id FROM links WHERE link="{}" """.format(url)
    #print(query)
    mycursor.execute(queryInsLink)
    mycursor.execute(queryGetId)
    linkId=mycursor.fetchone()[0]

    cnx.commit()
    
    cnx.close()
    return linkId

    ### Prüft, ob URL in DB vorhanden ist, wenn ja, returned False
def checkIfShouldCrawl(url):
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor()
    query="""SELECT EXISTS(SELECT id FROM links 
        WHERE link="{}")""".format(url)
    mycursor.execute(query)
    myresult = mycursor.fetchone()[0]

    cnx.close()
    if myresult==0: return True
    else: return False

## Schreibt alle Wörter in Liste in DB und stellt Wordlinks zu angegebener Link-ID her
def writeAllWords(words,siteId):
    cnx = mysql.connector.connect(**DBconfig)
    mycursor=cnx.cursor(buffered=True)
    queryInsWord="""INSERT INTO word (word) VALUES ("{}") ON DUPLICATE KEY UPDATE id=id """
    queryGetWId="""SELECT word.id FROM word WHERE word.word="{}" """
    queryInsWL="""INSERT INTO wordlinks(id_word,id_link) VALUES("{}","{}") ON DUPLICATE KEY UPDATE id=id """
    for word in words:
        mycursor.execute(queryInsWord.format(word))
        mycursor.execute(queryGetWId.format(word))
        wordId=mycursor.fetchone()[0]
        mycursor.execute(queryInsWL.format(wordId,siteId))
        cnx.commit()
    cnx.close()


    ### Crawled den angegebenen Link, die Tiefe dient zur limitierung
def crawlLink(startLink,currentDepth):
    global maxDepth
    print("Now crawling: {}".format(startLink))
    title=""
    allLinks=[]
    allImages=[]
    allWords=[]
    
    
    try:
        content = get_url_content(startLink)
    
        # übergebe html an beautifulsoup parser
        soup = BeautifulSoup(content, "html.parser")

        allLinks=getAllLinks(soup)
        #allImages=getAllImages(soup)
        allWords=getAllWords2(soup)
        title=getTitle(soup)
    except:
        # Fehler wie fehlender Titel,... werden abgefange
        print("An error occurred!")
        return False

    linkId=writeLinkToDB(startLink,title)

    ##In Lowercase konvertieren
    allWords=[w.lower() for w in allWords]

    print("Inserting {} words".format(len(allWords)))

    writeAllWords(allWords,linkId)
    


    if currentDepth<=maxDepth:

        for link in allLinks:

            if link.find(".css")!=-1 or link.find(".pdf")!=-1:
                continue   

            ## Format des Link prüfen, wenn ohne hostname-> diesen zufügen
            if link.startswith("/"):

                parsed_uri=urlparse(startLink)
                result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                link=result+link

            else:
                if link.startswith("http") or link.startswith("#"):
                    continue
                parsed_uri=urlparse(startLink)
                result = '{uri.scheme}://{uri.netloc}{uri.path}'.format(uri=parsed_uri)
                link=result+link
            

            ## Link crawlen
            shouldCrawl=checkIfShouldCrawl(link)
            if shouldCrawl:
                crawlLink(link,currentDepth+1)
             

### MAIN-Code

## Init Stopwords
##Source and more Information: https://solariz.de/de/downloads/6/german-enhanced-stopwords.htm
txt_file = open("stopwords.list", "r")
file_content = txt_file.read()

stopwords = file_content.split(",")
txt_file.close()

    
startSite=getStartSite()
if(startSite!=None):
    depth=0
    startLink=startSite[1]
    crawlLink(startLink,0)

           

    
    
else:
    print("Alle Datensätze aktuell, Web wird nicht gecrawled.")



