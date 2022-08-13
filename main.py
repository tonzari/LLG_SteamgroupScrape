import requests
from bs4 import BeautifulSoup

groupUrl = 'https://steamcommunity.com/groups/LanguageLearningGames'
groupPageResponse = requests.get(groupUrl)
groupPageHtml = BeautifulSoup(groupPageResponse.text, features='html.parser')
results = groupPageHtml.find_all('div', {'class': 'group_associated_game'})

textFile = open(f'games.txt', 'w')
print("Writing file... ")

for index, r in enumerate(results):
    gameTitle = r.text
    print(f"adding {index + 1}. {gameTitle.strip()}... ")
    communityUrl = r.find("a", recursive=False)['href']
    singleGameResponse = requests.get(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')
    result = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})
    storeUrl = result['href']
    textFile.write(f'{index + 1}, {gameTitle.strip()}, {storeUrl}' + '\n') 

textFile.close()
print("finished! file saved")