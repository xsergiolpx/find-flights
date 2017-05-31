### This python 3.x app is a dynamic web scrapper that scans the Kayak website to find the cheapest flight combinations between two airports in two given months.

### For example, if you want tom fly from Rome to Bangkok in July, and come back September, there are 900 possible date combinations. This app checks them all and gives back the best prices.

### To run the app use:

python desktop-version.py -d [month-departure] -r [month-return] -a [airport-code-departure] -b [airport-code-destination] -e [extension-of-kayak-webpace]

### Where the arguments can be:

### -d can be 01 or 02... up to 12
### -r can be also 01, 02... up to 12. Also here we can set it to 00 which means no return
### -a and -b take the airport code like BKK is Bangkok, or MAD is Madrid. Also you can use in the argument MAD,ROM instead of just ROM to use in the search both airports at the same time
### -e is the extension of the kayak website, it can be es for Spain, co.uk for UK, or you can use too es,co.uk to find in both domains the flights 

### Then run:

python analyze.py

### To get the results in the tsv file results.tsv

## One piece of warning is that Kayak do not like bots, so use with moderation and only for personal purposes if you do not want to get banned by IP level.
## To get this running make sure to have installed what's inside requirements.txt and Phantomjs