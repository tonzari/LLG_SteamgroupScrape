import requests
import json
from bs4 import BeautifulSoup

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

groupUrl = 'https://steamcommunity.com/groups/LanguageLearningGames'
groupPageResponse = requests.get(groupUrl)
groupPageHtml = BeautifulSoup(groupPageResponse.text, features='html.parser')
results = groupPageHtml.find_all('div', {'class': 'group_associated_game'})

games = []

jsonFile = open(f'games.json', 'w')
print("Writing file... ")

for index, r in enumerate(results):
    gameTitle = r.text
    print(f"adding {index + 1}. {gameTitle.strip()}... ")
    communityUrl = r.find("a", recursive=False)['href']
    singleGameResponse = requests.get(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')
    result = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})
    storeUrl = result['href']
    
    games.append(
        {
            'id': index,
            'title': {gameTitle.strip()},
            'storeUrl': storeUrl
        }
    )

jsonString = json.dumps(games, default=set_default)
jsonFile.write(jsonString) 

jsonFile.close()

print("finished! file saved")