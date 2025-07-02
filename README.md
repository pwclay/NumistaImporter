# NumistaImporter
Script to import collection data into numista 

This python script will import a csv file in the specified format into your Numista collection.  Note that the API is currently limited to 2000 calls per month, coin will take three calls to import, so you are limited to a maximum of 666 coins imported each month. The import process works in the following way:
1/ Change country name to Numista internal name - these are included in countries.csv
2/ Check for matches for country name, catalog type and catalog number. If there is only one match, the id of the match and description will be added to the file and the year is checked.
3/ Check of matches for the year, mint and type. If there is only one match for a year, it will be added even if the mintmark etc do not match.  If there are multiple matches for the specified data it will not be entered.  Match results are added to fullmatchid & partialmatchid
4/ Run the script with python3 process.py importdata.csv.  Note that the script will modify importdata.csv - keep a clean copy of your data in case of misadventure.

# Requirements:
1/ Numista API key & Client ID - update process.py with your API key & client IDobtained from here: https://en.numista.com/api/
2/ Import file in csv format as specified below
3/ countries.csv file updated with country names used and Numista code - this can be found by examining the url when searching the catalog - see this example for searching for New Zealand: https://en.numista.com/catalogue/index.php?e=nouvelle-zelande&r=&st=1-2-154-5-54&cat... countries.csv but be all lower case.
4/ Python3 installed on your machine.

# Import file format:
csv with the first row containing the following headers:
country - country name
nmcountry - country name used by Numista - filled by the script, if this column is blank after importing, the country name and Numista country name will need to be added to countries.csv
catcode - catalog code - currently KM & Y are supported.  Others can be added to process.py ~ line 150
codez - code number
matches - completed by script - the number of matches for the country, catalog & code
matchid - completed by script - if only one match, the Numista id for the coin is added
matchdesc - completed by script - if only one match, a description of the coin is added
cvalue - optional, useful to compare with matchdesc
denom - optional, useful to compare with matchdesc
descob - optional, useful to compare with matchdesc
descre - optional, useful to compare with matchdesc
comment - details of coin issue type, eg proof.  This is used inconsistently in Numista, for most coins & countries it is best left blank
year - year (local calendar preferred)
mintmark - mintmark of coin
fullmatchid - if year, comment and mintmark all match, this will be filled with the Numista id & the coin added to the collection
partialmatchid - if only year matches, this will be completed with the number of matches, unless there is only one, in which case this will be filled with the Numista id & the coin added to the collection
cond - condition of the coin - must be one of the options listed in conditions.csv, all
private_comment - this column will be added to the 'private comment' field in Numista
exclude - if this contains 'y', the line will be skipped by the script
entered - when a coin is added to the collection, this line will be 'y', and ignored on subsequent import attempts

# If it works:
Please send any additions to countries.csv back, preferably by a pull request in github so they can be used by the next person
Consider buying be a coffee (or alternative beverage) at: https://buymeacoffee.com/wekadesign
