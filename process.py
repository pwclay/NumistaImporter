api_key = 'YourAPIKey'
client_id = 'YourClientID'

###############################################################################
#                                                                             #
# Get coins based on country & catalog                                        #
#                                                                             #
###############################################################################


def gettype(coin):
    global api_key, base_url, catalogs
    # API call to search types by text
    response = requests.get(
      base_url + '/types',
      params={'issuer': coin['nmcountry'], 'catalogue': catalogs[coin['catcode']], 'number': coin['codez'], 'lang': 'en'},
      headers={'Numista-API-Key': api_key})
    search_results = response.json()
    # Check response code (simplified)
    if response.status_code==200:
      return search_results
    else:
      print("error in get type")
      print(search_results)
      print(coin)
      search_results="error"
      return search_results


###############################################################################
#                                                                             #
# match years for a coin type                                                 #
#                                                                             #
###############################################################################


def getissues(coin):
    global api_key, base_url
    matches = {}
    matches['full'] = []
    matches['partial'] = []

    # API call to search types by text
    response = requests.get(
      base_url + '/types/' + coin['matchid'] + '/issues/',
      params={'lang': 'en'},
      headers={'Numista-API-Key': api_key})
    search_results = response.json()
    # Check response code (simplified)
    if response.status_code==200:
      # Display search results
      for row in search_results:
          if row['is_dated'] == False:
              row['year'] =0
          if 'mint_letter' not in row:
              row['mint_letter']=''
          if 'comment' not in row:
              row['comment']=''

          if row['year'] == int(coin['year']) and row['mint_letter'] == coin['mintmark'] and row['comment'] == coin['comment']:
              #full match of data
              matches['full'].append(row['id'])
          else:
              if row['year'] == int(coin['year']):
                    matches['partial'].append(row['id'])
    else:
      print("error in get issues")
      print(search_results)
      print(coin)
      matches="error"

    return matches

###############################################################################
#                                                                             #
# add coin to your collection                                                 #
#                                                                             #
###############################################################################

def addcoin(coin,addtype):
    # API call to add to the collection
    postdata={'type': coin['matchid'],
            'issue': addtype}
    if coin['cond'] !='':
        if coin['cond'].lower() in conditions:
            postdata['grade'] = conditions[coin['cond'].lower()]
    if coin['private_comment'] !=None and coin['private_comment'] !='':
        postdata['private_comment'] = coin['private_comment']

    response = requests.post(
      base_url + '/users/' + str(client_id) + '/collected_items',
      json=postdata,
      headers={'Numista-API-Key': api_key, 'Authorization': 'Bearer '+ access_token})
    addcoin = response.json()
    if response.status_code==201:
      print('Added '+coin['country'] + coin['matchdesc'])
      result = 1;
    else:
      result = 0;
      if response.status_code==429:
          print("Quota reached")
    return result
    conditions[row['condition']] = row['nmcondition']

###############################################################################
# This is an example to illustrate how to use                                 #
# the Numista API in Python.                                                  #
#                                                                             #
# The processing is simplified for illustrative                               #
# purpose. It should not be used for real applications                        #
# without considering all possible cases, espcially                           #
# error cases.                                                                #
###############################################################################

import requests
import sys
import csv
from uuid import uuid4

# Parameters
base_url = 'https://api.numista.com/v3'
conditions_file = 'conditions.csv'
countries_file = 'countries.csv'


#load conditions translation from csv - numista only has a limited number of acceptable conditions
conditions = {}

with open(conditions_file, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        conditions[row['condition']] = row['nmcondition']

print("Conditions loaded")

#load countries translation from csv - coin lookups need to be with the country name numista uses
countries = {}

with open(countries_file, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        countries[row['country']] = row['nmcountry']

print("Countries loaded")

# list of catalogs and numista code, more can be added
catalogs = {
  "KM": 3,
  "KM#": 3,
  "Y":  9,
  "Y#": 9
  }

if len(sys.argv) > 1:
    collection_file = sys.argv[1]  # First argument (after the script name)
    print("Using file:", collection_file)
else:
    print("No command-line arguments provided.")
    sys.exit(1)

# Authenticate for own collection

response = requests.get(
  base_url + '/oauth_token?grant_type=client_credentials&scope=view_collection,edit_collection',
  params={'lang': 'en'},
  headers={'Numista-API-Key': api_key})
key = response.json()
print(key)
print("key obtained")
access_token = key['access_token']

# API call to get the collection
response = requests.get(
  base_url + '/users/' + str(client_id) + '/collected_items',
  params={'lang': 'en'},
  headers={'Numista-API-Key': api_key, 'Authorization': 'Bearer '+ access_token})
userdata = response.json()
print(f"{userdata['item_count']} Coins in collection")

#load collection file from csv, it will likely need to be processed multiple times

with open(collection_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    collection = list(reader)  # List of dicts: one per row

for row in collection:
    if row['country'].lower() in countries:
        row['nmcountry'] = countries[row['country'].lower()]
    if row['exclude'].lower()!='y' and row['entered'].lower()!='y':
        #Look up coin data
        if row['nmcountry']!='' and row['matches']=='' and row['catcode'] in catalogs:
            #We have a valid country and catalog but no match data, look up coin
            typeresult = gettype(row)
            if typeresult == "error":
                #there was an error, probably we have reached the quota, break out of the loop
                break
            row['matches'] = typeresult['count']
            if int(typeresult['count']) == 1:
                #We have only one match for the country & catalog code, so we will add the numista type to the file, along with the description to confirm it is correct manually
                row['matchid']= str(typeresult['types'][0]['id'])
                row['matchdesc']= typeresult['types'][0]['title']

        if row['matchid'] != '' and row['matchid'] != None and (row['fullmatchid']=='' and row['partialmatchid']==''):
            #we have a type match, check for year matches
            print('checking years')
            issueresult=getissues(row)
            if issueresult == "error":
                #there was an error, probably we have reached the quota, break out of the loop
                break

            if len(issueresult['full']) == 1:
                row['fullmatchid']=issueresult['full'][0]
            else:
                if len(issueresult['full']) > 1:
                    row['fullmatchid'] = "matches:" + str(len(issueresult['full']))
                else:
                    if len(issueresult['partial']) == 1:
                        row['partialmatchid']=issueresult['partial'][0]
                    else:
                        if len(issueresult['partial']) > 1:
                            row['fullmatchid'] = "matches:" + str(len(issueresult['partial']))

            if row['fullmatchid']!='' or row['partialmatchid']!='':
                if isinstance(row['fullmatchid'], (int, float)):
                    #We only have one full match, add it to the collection
                    if addcoin(row,row['fullmatchid']) == 1:
                        row['entered'] = "y"
                    else:
                        #there was an error adding the type, probably we have reached the quota, break out of the loop
                        break
                else:
                    if isinstance(row['partialmatchid'], (int, float)):
                      #We only have one partial match, add it to the collection
                      if addcoin(row,row['partialmatchid']) == 1:
                          row['entered'] = "y"
                      else:
                          #there was an error adding the type, probably we have reached the quota, break out of the loop
                          break

    else:
        #row already entered or marked to exclude
        print('exclude row')


#save collection file with updated data
fieldnames = collection[0].keys()  # or manually specify the order
with open(collection_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()  # Write the header row
    writer.writerows(collection)  # Write all the data rows
