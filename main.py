import requests
from bs4 import BeautifulSoup

groupUrl = 'https://steamcommunity.com/groups/LanguageLearningGames'

groupPageResponse = requests.get(groupUrl)

groupPageHtml = BeautifulSoup(groupPageResponse.text, features='html.parser')

results = groupPageHtml.find_all('div', {'class': 'group_associated_game'})

for r in results:
    gameTitle = r.text
    communityUrl = r.find("a", recursive=False)['href']
    singleGameResponse = requests.get(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')
    result = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})
    storeUrl = result['href']
    print(gameTitle + ': ' + storeUrl)

# The link returned is a community page link.
# Next, scrape that URL to get the store page link