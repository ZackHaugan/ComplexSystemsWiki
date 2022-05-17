from bs4 import BeautifulSoup as bs
import requests
import lxml
import urllib
import csv
import json


# globals
queue = []
searched = set()
original = {}

# start session object
session = requests.session()


def loading_bar(pretext:str, current:int, total:int, barWidth=50) -> None:
    print(f"\r{' '*(len(pretext)+len(str(current))+len(str(total))+barWidth+7+9+0)}",end='')
    print(f"\r{pretext} ({current}/{total}): [{(('█'*((barWidth*current)//total))+[[' ','▏','▎','▍','▌','▋','▊','▉'][((8*barWidth*current)//total)%8],''][current==total]).ljust(barWidth)}] {round(100*current/total,2)}%", end=['','\n'][current==total])


def getJson():
    global original
    global queue
    with open('data.json', 'r') as f:
        data = json.load(f)
    original = data['original']
    queue = data['queue']


def saveJson():
    with open('data.json', 'w') as f:
        json.dump({
            "original":original,
            "queue":queue}, f)


def addConnections(connection_dict):
    """list of dicts in form parent:[child1, child2, ...]"""
    with open('connections.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Source","Target","Weight"])
        for parent, children in connection_dict.items():
            for child in children:
                writer.writerow({"Source":parent,
                            "Target":child,
                            "Weight":1})

def isValidWikiLink(link):
    
    if link.startswith('/wiki/'):
        # validate Wikipedia links by excluding those that contain a blacklisted tag (wiki links that aren't real articles)
        for tag in ['special:', 'user:', 'wikipedia:', 'wp:', 'project:', 'file:', 'image:', 'mediawiki:', 'template:', 'help:', 'category:', 'portal:', 'draft:', 'timedtext:', 'module:', 'wikipedia_talk:', 'wt:', 'cat:', 'h:', 'mos:', 'p:', 't:', 'draft:', 'talk:', 'project_talk:', 'image_talk:', 'file_talk:', 'template_talk:', 'user_talk', 'book:']:
            if link[6:].lower().startswith(tag):
                return False
        return True
    return False


def getRealTitle(page):
    link = f"https://en.wikipedia.org/wiki/{page}"
    webpage = session.get(link)
    return webpage.url[30:]


def getChildren(page, check_titles=True):
    link = f"https://en.wikipedia.org/wiki/{page}"
    webpage = bs(session.get(link).text, 'lxml')
    article = webpage.find_all('div', {"class":"mw-parser-output"}, limit=1)

    if len(article)==0:
        return []

    children = set()

    useful = article[0].find_all('p')
    for p_tag in useful:
        allLinks = [str(link.get('href')) for link in p_tag.find_all("a")]
        for link in allLinks:
            if isValidWikiLink(link):
                pound_location = link.find('#',6)
                if check_titles:
                    if pound_location==-1:
                        real_title = getRealTitle(link[6:])
                    else:
                        real_title = getRealTitle(link[6:pound_location])
                else:
                    real_title = link[6:] if pound_location==-1 else link[6:pound_location]
                children.add(real_title)
    return children


def search(page_batch=10, check_titles=True):
    global queue
    all_set = set(original.keys())
    counter = 998-len(queue)
    connection_dict = {}

    while len(queue)>0:
        if counter % page_batch == 0 and counter != 0:
            print(f"\rAdding {page_batch} new pages to connections ({counter} total){' '*20}")
            addConnections(connection_dict)
            saveJson()
            connection_dict = {}
        
        parent = queue[0]
        queue.pop(0)
        print(f"\rSearching page '{parent[:30]}' ({counter}/998){' '*(50-len(parent))}", end='')
        children = getChildren(parent, check_titles)
        real_children = all_set & children
        connection_dict[parent] = real_children
        counter += 1
    
    addConnections(connection_dict)
    saveJson()

    print("\nNo more pages to search")
    

def getOriginal():
    global original
    global queue
    link = "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles"
    webpage = bs(session.get(link).text, 'lxml')
    article = webpage.find_all('div', {"class":"mw-parser-output"}, limit=1)[0]
    sections = article.find_all('table', {"class":"multicol"})
    
    # order of sections:
    section_labels = ["People", "History", "Geography", "Arts", "Philosophy and Religion", "Everyday Life", "Society", "Health", "Science", "Technology", "Mathematics"]

    for i, label in enumerate(section_labels):
        sectionLinks = [str(link.get('href')) for link in sections[i].find_all("a")]
        for link in sectionLinks:
            if isValidWikiLink(link):
                pound_location = link.find('#',6)
                if pound_location==-1:
                    real_title = getRealTitle(link[6:])
                else:
                    real_title = getRealTitle(link[6:pound_location])
                original[real_title] = label
    print(f"Count of Original Articles: {len(original)}")
    queue = list(original.keys())
    saveJson()

def makeNodes():
    getJson()
    classes_dict = {"People":0, "History":1, "Geography":2, "Arts":3, "Philosophy and Religion":4, "Everyday Life":5, "Society":6, "Health":7, "Science":8, "Technology":9, "Mathematics":10}
    with open("nodes.csv", 'w', newline='',  encoding='utf-8') as f:
        field_names = ['Id', 'Label', 'class']
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for page, class_name in original.items():
            writer.writerow({
                'Id':page,
                'Label':urllib.parse.unquote(page).replace("_"," "),
                'class':classes_dict[class_name]
            })




# getJson()
# makeNodes()

# queue = list(original.keys())
# search(20, False)

# print(urllib.parse.unquote("%C3%B3"))


# https://en.wikipedia.org/wiki/Wikipedia:Vital_articles 
# 1000 vital wikipedia articles

