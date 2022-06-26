import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urlparse
from io import StringIO
from html.parser import HTMLParser
import re
import validators
import time

### DB-Parameter
DBconfig = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'searchengine',
  'raise_on_warnings': True
}

maxDepth=2

## Liste der zu entfernenden Sonderzeichen, kann bei bedarf ergänzt werden
specialsymbols = "!@#$%^&*()_+={[}]|\;:\"<>?/., '\"©►“„…´​​​​​​"


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
## wird derzeit nicht genutzt
def getAllImages(soup):
    images=[]
    
    for img in soup.findAll('img'):
        images.append(img.get('src'))
        #print("Found the Image:", img.get('src'))
    return images

## Gibt den Titel der Website zurück
def getTitle(soup):    
    ## leerzeichen in titel erlaubt!
    symbols = specialsymbols.replace(" ","")
    title=soup.title.text
    for i in range(len(symbols)):
       title = title.replace(symbols[i], "")
    return title


## RegEx für Telefonnummern
regexTel= "[\+0\/][0-9 .()-]+"

## RegEx für URLs, angepasst aus Internet, da keine perfekte Lösung gefunden wurde
regexURL = re.compile(r"(\w+:\/\/)?(\w+\.)?(([a-zA-Z]+\w*)\.(\w+))(\.\w+)*([\w\-\._\~\/]*)*(?<!\.)[^.]")

## Wörter der Seite extrahieren, filtert auch Telefonnummern, E-Mails&URLs
def getAllWords(soup):
    wordset={""}
    telNrs={""}
    for each_text in soup.findAll("p"):
        if each_text is not None: 
            words=[]

            content = each_text.text

            ## Telefonnummern vorfiltern
            ## Werden extra Liste angefügt, um Ersetzung von Sonderzeichen zu umgehen, am ende wieder an ausgabeliste angefügt
            numbers=re.findall(regexTel,content)
            if numbers: 
               for n in numbers: content=content.replace(n," ")
               n=n.replace(" ","")
               telNrs.add(n)

            ## Aufteilung des Paragraphen in einzelne Wörter
            words = content.lower().split()

            for word in words:
                ## - am Anfang des wortes entfernen
                if word.startswith("-"):
                    word=word[1:]
                ## - am Ende des Wortes entfernen
                if word.endswith("-"):
                    word=word[:-1]
                ##  E-Mail-Adressen entfernen -> Erweiterungsmöglichkeit: Tabelle für Kontaktdaten..?
                if(re.search(r"[\w\.\+\-]+\@[\w-]+(?:.[\w-])*\.[a-z]{2,3}", word)):
                        print("email found: {}".format(word))
                        words.remove(word)
                        continue
                ## URLs entfernen
                if regexURL.match(word) is not None:
                    print("url erkannt: "+word)
                    while word in words: words.remove(word)
                    continue
            ## Wordset mit gefilterten Wörtern des Paragraphen updaten -> keine Duplikate, da Set    
            wordset.update(words)

    ## Stoppwortbereinigung
    wordset=removeStopWords(wordset)

    ## Sonderzeichen aus Wortliste bereinigen
    cleanWordlist=clean_wordlist(list(wordset))

    ## lleerer Datensatz aus TelNr-Liste löschen (notwendig, da sonst immer probleme...
    telNrs.remove("")
    ## Listen zusammenfügen
    if len(telNrs)>=0: cleanWordlist.extend(list(telNrs))
    return cleanWordlist

 ##Stoppwörter löschen (mit Messung&Ausgabe der Anzahl)
def removeStopWords(wordset):
    len1=len(wordset)
    wordset=wordset-set(stopwords)
    len2=len1-len(wordset)
    print("removed {} stopwords".format(len2))
    return wordset

## Reinigt die Liste von Sonderzeichen
def clean_wordlist(wordlist):
    clean_list = []
    for word in wordlist:
        for i in range(len(specialsymbols)):
            word = word.replace(specialsymbols[i], "")
        if len(word) > 0:
            clean_list.append(word)
    return clean_list


## Holt Seite von der DB, welche am längsten nicht gecrawled wurde, jedoch in den letzten 24h noch nicht
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
    mycursor.execute(queryInsLink)
    mycursor.execute(queryGetId)
    linkId=mycursor.fetchone()[0]

    cnx.commit()
    
    cnx.close()
    return linkId

    ### Prüft, ob URL in DB vorhanden ist, wenn ja, returned False, da diese später automatisch gecrawled wird
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
    queryInsWord="""INSERT INTO words (word) VALUES ("{}") ON DUPLICATE KEY UPDATE id=id """
    queryGetWId="""SELECT words.id FROM words WHERE words.word="{}" """
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
        allWords=getAllWords(soup)
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
    

    ## Tiefenbegrenzung: Damit Crawler nicht ewig auf einer Seite unterlinks crawled wird Begrenzung dann aktiv, tiefere Seiten werden nur langsam dem Crawler zugefügt
    if currentDepth<=maxDepth:
        filetypes=[
            ".css",
            ".pdf",
            ".zip",
            ".jpg",
            ".doc"
            ]    

        for link in allLinks:

            ## Dateien wie .css, .pdf, .zip, .jpg nicht crawlen!!
            isbadlink=False
            for ft in filetypes:
                if(link.find(ft)!=-1):
                    isbadlink=True  
            if isbadlink: continue

            ## Tel & Mail-Links überspringen
            if link.startswith("tel:") or link.startswith("mailto"):
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

print("Starting MV and JF's WebCrawler!")

## Init Stopwords
##Source and more Information: https://solariz.de/de/downloads/6/german-enhanced-stopwords.htm
stopwords=[]
try:
    txt_file = open("stopwords.list", "r")
    file_content = txt_file.read()

    stopwords = file_content.split(",")
    txt_file.close()
except:
    print("Stoppwortliste nicht gefunden! Es werden keine Stoppworte gefiltert!")


while(1):   
    startSite=getStartSite()
    if(startSite!=None):
        depth=0
        startLink=startSite[1]
        crawlLink(startLink,0)

    else:
        print("Alle Datensätze aktuell, Web wird nicht gecrawled.")
        time.sleep(5)



