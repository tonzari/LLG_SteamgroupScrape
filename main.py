import requests
import json
from bs4 import BeautifulSoup

# Helper function: https://stackoverflow.com/questions/22281059/set-object-is-not-json-serializable
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

# Set Steam Group URL, find the associated games list, store it in results
groupUrl = 'https://steamcommunity.com/groups/LanguageLearningGames'
groupPageResponse = requests.get(groupUrl)
groupPageHtml = BeautifulSoup(groupPageResponse.text, features='html.parser')
results = groupPageHtml.find_all('div', {'class': 'group_associated_game'})

games = []

jsonFile = open(f'games.json', 'w')
print("\nWriting file...\n")

for index, r in enumerate(results):
    print(f"adding {index + 1}. {r.text.strip()}... ", end=" ")
    communityUrl = r.find("a", recursive = False)['href']
    singleGameResponse = requests.get(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')
    aTag = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})
    titleTag = gamePageHtml.find('div', {'class': 'apphub_AppName'})
    gameTitle = titleTag.text.strip()
    storeUrl = aTag['href'].split('?')[0]   # Split store URL at ? mark to remove personalized identification number

    # Get single game store page html
    storePageResponse = requests.get(storeUrl)
    storePageHtml = BeautifulSoup(storePageResponse.text, features="html.parser")
    
    # Get game store image url
    imgTag = storePageHtml.find('img', {'class': 'game_header_image_full'})
    imgSrc = imgTag['src'].split('?')[0]
    
    # Get game store description snippet
    descTag = storePageHtml.find('div', {'class': 'game_description_snippet'})
    description = descTag.text.strip()

    # Get game store release date
    dateTag = storePageHtml.find('div', {'class': 'date'})
    releaseDate = dateTag.text.strip()
    
    games.append(
        {
            'id': index + 1,
            'description': description,
            'title': gameTitle,
            'releaseDate': releaseDate,
            'storeUrl': storeUrl,
            'imageUrl': imgSrc
        }
    )
    print("done!")

jsonString = json.dumps(games, default = set_default, indent = 4)
jsonFile.write(jsonString) 

jsonFile.close()

print("\nFinished! File saved.\n")