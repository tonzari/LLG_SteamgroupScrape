import requests
from bs4 import BeautifulSoup

url = 'https://steamcommunity.com/groups/LanguageLearningGames'

response = requests.get(url)

soup = BeautifulSoup(response.text, features='html.parser')

results = soup.find_all('div', {'class': 'group_associated_game'})

for r in results:
    atag = r.find("a", recursive=False)
    name = r.text
    print(name + ': ' + atag['href'])

# The link returned is a community page link.
# Next, scrape that URL to get the store page link