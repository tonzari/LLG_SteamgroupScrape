import requests
import json
import time
from bs4 import BeautifulSoup

# Helper function: https://stackoverflow.com/questions/22281059/set-object-is-not-json-serializable
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

# Attempt to get page response, and retry if server error is returned. Lately Steam has been throwing server errors!
def try_get_page(url, retries=5, wait_time=5):
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

# Attempt to get image. Some games don't have images, even though they are required by Steam. Fallback to placehoder or other Steam image.
def try_get_image_or_fallback(url, fallback_url):
    try:
        response = requests.head(url)

        # Check if the status code is in the 2xx range (successful)
        if response.status_code // 100 == 2:
            return url
        else:
            print(f"Image URL is not valid, status code: {response.status_code}")
            return fallback_url
    except requests.exceptions.RequestException as e:
        print(f"Error checking image URL: {e}")
        return fallback_url

# Empty array to store games and developers
games = []
developers = []

# Set Steam Group URL, Get page, parse HTML
groupUrl = 'https://steamcommunity.com/groups/LanguageLearningGames'
groupPageResponse = requests.get(groupUrl)
groupPageHtml = BeautifulSoup(groupPageResponse.text, features='html.parser')

# find individual associated games (from the panel), and store all found in results variable
results = groupPageHtml.find_all('div', {'class': 'group_associated_game'})

# Prepare json file to store game data in
jsonFile = open(f'games.json', 'w', encoding='utf-8')
devsJsonFile = open(f'developers.json', 'w', encoding='utf-8')

print("\nWriting file...\n")

# Begin looping through all Associated Games
for index, result in enumerate(results):

    print(f"adding {index + 1}. {result.text.strip()}... ", end=" ")

    # Get URL to game (this is a community page URL)
    communityUrl = result.find("a", recursive = False)['href']

    # Parse HTML of community page
    singleGameResponse =  try_get_page(communityUrl)
    gamePageHtml = BeautifulSoup(singleGameResponse.text, features='html.parser')

    # Find game title
    titleTag = gamePageHtml.find('div', {'class': 'apphub_AppName'})
    gameTitle = titleTag.text.strip()

    # Find game store URL
    aTag = gamePageHtml.find('a', {'id': 'app_header_view_store_page_btn'})

    # Split store URL at ? mark to remove personalized identification number
    storeUrl = aTag['href'].split('?')[0]   

    # Parse HTML of store page
    storePageResponse = try_get_page(storeUrl)
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

    # Find game developers
    developersTag = storePageHtml.find('div', {'id': 'developers_list'})
    devAnchorTags = developersTag.find_all('a')
    devs = []

    for devIndex, devTag in enumerate(devAnchorTags):
        
        devs.append(
            {
                'id': devIndex + 1,
                'link': devTag['href'],
                'name': devTag.text.strip()
            }
        )

        developer = {
            'link': devTag['href'],
            'name': devTag.text.strip()
        }

        if developer not in developers:
            developers.append(developer)


    # Find game app id to build library image urls
    gameAppId = storeUrl.split("/")[4]
    libImgSrc =  try_get_image_or_fallback(f'https://steamcdn-a.akamaihd.net/steam/apps/{gameAppId}/library_600x900_2x.jpg', imgSrc)
    libHeroImgSrc = try_get_image_or_fallback(f'https://steamcdn-a.akamaihd.net/steam/apps/{gameAppId}/library_hero.jpg', imgSrc)
    libLogoImgSrc = try_get_image_or_fallback(f'https://steamcdn-a.akamaihd.net/steam/apps/{gameAppId}/logo.png', f'https://via.placeholder.com/400x400?text={gameTitle}')
    
    games.append(
        {
            'id': index + 1,
            'description': description,
            'title': gameTitle,
            'releaseDate': releaseDate,
            'storeUrl': storeUrl,
            'imageUrl': imgSrc,
            'libraryImageUrl': libImgSrc,
            'libraryHeroImageUrl': libHeroImgSrc ,
            'libraryLogoImageUrl': libLogoImgSrc,
            'developers': devs
        }
    )
    print("done!")


# add id to each developer
for devListIndex, d in enumerate(developers):
    d['id'] = devListIndex + 1

# convert to json, write to file, close
jsonString = json.dumps(games, default = set_default, ensure_ascii=False, indent = 4)
jsonFile.write(jsonString) 
jsonFile.close()

devsJsonString = json.dumps(developers, default = set_default, ensure_ascii=False, indent = 4)
devsJsonFile.write(devsJsonString)
devsJsonFile.close()

print("\nFinished! File saved.\n")

# todo: 
# handle missing library images (capsule and hero)
# if capsule is missing, use store image centered, but fill background with color gradient
# if hero is missing, grab store screenshot image
# if logo is missing, generate placeholder?  
# https://via.placeholder.com/600x400/{hex for background}}/{hex for text color}}?text=asdasd 
# https://placehold.jp/3d4070/ffffff/150x150.png?text=hashdsad%20%20%20hasdh%20hahdas%200hh