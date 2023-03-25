import requests
import json
import time
from bs4 import BeautifulSoup

# Helper function: https://stackoverflow.com/questions/22281059/set-object-is-not-json-serializable
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def get_page(url, retries=5, wait_time=5):
    for i in range(retries):
        try:
            response = requests.get(url)

            # Check if the status code indicates success (2xx)
            if response.status_code // 100 == 2:
                return response
            else:
                print(f"Unexpected error, status code: {response.status_code}. Retrying... ({i + 1}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying... ({i + 1}/{retries})")

        # Wait before trying again
        time.sleep(wait_time)

    # If all retries failed, return None
    return None

def get_valid_image_url(url, fallback_url):
    try:
        response = requests.head(url)

        # Check if the status code is in the 2xx range (successful)
        if response.status_code // 100 == 2:
            print(f"Image URL is valid: {url}")
            return url
        else:
            print(f"Image URL is not valid, status code: {response.status_code}")
            return fallback_url
    except requests.exceptions.RequestException as e:
        print(f"Error checking image URL: {e}")
        return fallback_url

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

    # Get URL to game (this is a community page URL)
    communityUrl = r.find("a", recursive = False)['href']

    # Parse HTML of community page
    singleGameResponse =  get_page(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')

    # Fint game title
    titleTag = gamePageHtml.find('div', {'class': 'apphub_AppName'})
    gameTitle = titleTag.text.strip()

    # Find game store URL
    aTag = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})

    # Split store URL at ? mark to remove personalized identification number
    storeUrl = aTag['href'].split('?')[0]   

    # Parse HTML of store page
    storePageResponse = get_page(storeUrl)
    storePageHtml = BeautifulSoup(storePageResponse.text, features="html.parser")
    
    # Find game store image url
    imgTag = storePageHtml.find('img', {'class': 'game_header_image_full'})
    imgSrc = imgTag['src'].split('?')[0]
    
    # Find game store description snippet
    descTag = storePageHtml.find('div', {'class': 'game_description_snippet'})
    description = descTag.text.strip()

    # Find game store release date
    dateTag = storePageHtml.find('div', {'class': 'date'})
    releaseDate = dateTag.text.strip()

    # Find game app id to build library image url
    gameAppId = storeUrl.split("/")[4]
    libImgSrc =  get_valid_image_url(f'https://steamcdn-a.akamaihd.net/steam/apps/{gameAppId}/library_600x900_2x.jpg', imgSrc)
    
    games.append(
        {
            'id': index + 1,
            'description': description,
            'title': gameTitle,
            'releaseDate': releaseDate,
            'storeUrl': storeUrl,
            'imageUrl': imgSrc,
            'libraryImageUrl': libImgSrc
        }
    )
    print("done!")

jsonString = json.dumps(games, default = set_default, indent = 4)
jsonFile.write(jsonString) 

jsonFile.close()

print("\nFinished! File saved.\n")

## Save all images


# to do
# get library assets:
# --  https://steamcdn-a.akamaihd.net/steam/apps/<APP_ID>/library_600x900_2x.jpg
# --  https://steamcdn-a.akamaihd.net/steam/apps/<APP_ID>/library_hero.jpg