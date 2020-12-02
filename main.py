from configparser import ConfigParser
import pymongo
from pymongo import MongoClient
import pprint
import requests
import json
import time
import random
import re
from Atlas_Connection import Atlas_Connect
cluster = MongoClient(Atlas_Connect)
Itemdb = cluster["POE_DOCS"]
currencyCollection = Itemdb["Currency"]
cardsCollection = Itemdb["Cards"]
accessoriesCollection = Itemdb["accessories"]
gemsCollection = Itemdb["gems"]
jewelsCollection = Itemdb["Jewels"]
mapsCollection = Itemdb["Maps"]
weaponsCollection = Itemdb["weapons"]
armourCollection = Itemdb["armour"]
flaskCollection = Itemdb["flasks"]
################
###Categories###
################
# Currency
# SubCat: resonator

# Cards
# No base Type

# accessories
# SubCat: ring, amulet, belt, trinket,

# gems
# SubCat: activegem, supportgem

# jewels
# SubCat: abyss, cluster,

# maps
# SubCat: fragment, scarab,

# weapons
# SubCat: staff, onesword, dagger, wand, twoaxe, twosword, twomace, bow, onemace, sceptre, claw, dagger, oneaxe, twoaxe,

# armour
# SubCat: chest, helmet, gloves, boots, quiver, shield

# heistequipment
# SubCat: heistreward, contract, heisttool, heistweapon, heistutility,


def sweez():
    a = 'a'
    return


def get_price_override(stashname):
    priceRegex = "~price [\S]+ [\S]+"
    buyOutRegex = "~b/o [\S]+ [\S]+"
    try:
        if '~price' in stashname:
            matches = re.match(priceRegex, stashname, re.MULTILINE)
            # Trim the first match to cut off '~price '
            stashprice = matches[0][7:]
            return stashprice
        elif '~b/o' in stashname:
            matches = re.match(buyOutRegex, stashname, re.MULTILINE)
            # Trim the first match to cut off '~b/o '
            stashprice = matches[0][5:]
            return stashprice
    except TypeError:
        pass


def post(item_length, list_items, priceoverride):
    x = 0
    list_index['stash']
    keylist = ['icon', 'name', 'stackSize', 'identified', 'descrText', 'ilvl',
               'explicitMods', 'implicitMods', 'note', 'baseType', 'typeLine', 'flavourText', 'x', 'y', 'corrupted', 'properties', 'sockets', 'influences', 'requirements']

    while x < item_length:
        items_in_index = list_items[x]
        Post = {}
        for key in keylist:
            try:
                Post[key] = items_in_index[key]
            except KeyError:
                continue
        extended = items_in_index["extended"]
        try:
            subcategories = extended['subcategories']
            Post['subcategories'] = extended['subcategories']
        except KeyError:
            pass
        # If item is not priced, try assigning a tab-wide price
        try:
            if priceoverride != None and items_in_index['note'] == '':
                Post['note'] = priceoverride
        except KeyError:
            if priceoverride != None:
                Post['note'] = priceoverride

        # Define dictionary to use in insert_one command (Currently incomplete list)
        collections = {
            'currency': currencyCollection,
            'cards': cardsCollection,
            'accessories': accessoriesCollection,
            'gems': gemsCollection,
            'jewels': jewelsCollection,
            'maps': mapsCollection,
            'weapons': weaponsCollection,
            'armour': armourCollection,
            'flasks': flaskCollection
        }
        # Reference the above dictionary to add the item data to the appropriate collection
        if extended['category'] not in ['heistequipment']:
            sweez()
            collections[extended['category']].insert_one(Post)

        x += 1
    return


while True:  # loops infinitely
    # stops for 600 milleseconds so app doest get rate limited
    time.sleep(.600)
    # opens txt file and reads change id
    with open("next_change_id.txt") as file:
        change_id = file.read()
        # api response with the change id
        response = requests.get(
            "http://www.pathofexile.com/api/public-stash-tabs?id=" + change_id)
        file.close()
        # reads the response and formats as json
        json_response = response.json()
        # gets the next change id
        next_change_id = json_response['next_change_id']
        # if the next change id is the same as the current if moves on so the app doesnt process the same data
        if next_change_id == change_id:
            continue
        # gets all the stash tab data from api response
        json_data = json_response["stashes"]
        list_length = len(json_data)
        # opens file and writes next change id to the file
        f = open("next_change_id.txt", "w")
        f.write(next_change_id)
        f.close()
        x = 0
        while x < list_length:
            # loops trough the stash data list
            list_index = json_data[x]
            # filters out anything but the league you are wanting data from
            # this can be anything before items in the json data or nothing at all it just makes the data alot smaller
            if list_index['league'] == 'Heist':
                stashname = list_index['stash']
                if '~' in stashname:
                    priceoverride = get_price_override(stashname)
                else:
                    priceoverride = ''
                # priceoverride(list_index['Stash'])
                # ETHICAL LEAGUE (PL12057)
                # grabs all the item data form the stashes in that what ever filter you set
                list_items = list_index['items']
                # gets length of the item data list
                item_length = len(list_items)
                # loops through the item list
                post(item_length=item_length,
                     list_items=list_items, priceoverride=priceoverride)

            x += 1
        # writes next change id to the file so it can be on the current shard
        with open('next_change_id.txt', 'w') as file:
            file.write(next_change_id)
