import re
regex = re.compile(
    r"(\w+:\/\/)?(\w+\.)?(([a-zA-Z]+\w*)\.(\w+))(\.\w+)*([\w\-\._\~\/]*)*(?<!\.)[^.]"
)

cases=[
    "www.graduatecampus.de/bachelor/studiengaenge/sozialmana",
    "www.heidenheim.dhbw.de/last-minute-studienplaetze",
    "www.heidenheim.dhbw.de/coronavirus",
    "www.instagram.com/stuvheidenheim",
    "www.cas.dhbw.de/studiengebuehren",
    "https://...",
    "https://..",
    "https://.",
    "https://.google.com",
    "https://..google.com",
    "https://...google.com",
    "https://.google..com",
    "https://.google...com"
    "https://...google..com",
    "https://...google...com",
    "google.com",
    ".google.co.",
    "2.4",
    "e.v.",
    "www.dhbw.de",
    "www.heidenheim.dhbw.de //"
    
    ]

for c in cases:
    #print(c, regex.match(c).span()[1] - regex.match(c).span()[0] == len(c))

    print(regex.match(c) is not None)
