# twit_imposter_finder
interactive python3 cli script, which finds twitter accounts impersonating other people, then reports and blocks them. 

## why use this?
the script uses selenium to actually replicate a human being's methods of executing reporting and blocking a user. 

## why not just use twitter's API?
* they asks for a phone number
* there is a possiblity you may not get the authentication codes
* actually reports with reason, rather than ambiguous reporting
* this is much harder challenge for me personally

# how to use?
code is tested on python 3.8.6

preferably you would create a virtualenv

```bash
# clone git
git clone https://github.com/crypt0miester/twit_imposter_finder.git

# change directory
cd twit_imposter_finder

# create virtual environment
virtualenv env

# activate environment
source env/bin/activate

# install requirements like below
```

## requirement

* Python 3
* selenium==3.141.0
* imagehash
* sqlalchemy
* sqlalchemy-utils
* pyopenssl
* ndg-httpsclient
* pyasn1
* urllib3

```bash
pip install -r requirements.txt
```

## run the code

```bash
python3 main.py
```

## questions asked by the interactive script

* username
* password - obviously

* report reason - twitter asks for reason for reporting, when actually reporting the imposter
* fetch profile - you may opt out to not fetch your own profile for reruns
* test mode - creates a report/list in an excel sheet (.csv format) and does not report the imposters

* 2fa - if 2fa is enabled, the script will ask for the 6 digits when the page comes to view. please click on the terminal when this is asked.

## how does the script screen imposters
firstly, it screens based on profile name of the searched twitter account. secondly, it will then match the profile image of the imposter. thirdly, it will report and block the scammer.
the script currently uses [Imagehash by JohannesBuchner's](https://github.com/JohannesBuchner/imagehash) average hashing method, which is able to recognize images easily and store it in low bytes in the db.

# note
I do acknowledge that twitter does not allow scarping. but a lot of people don't want to use twitter's dev API due to it asking for phone numbers.
hopefully twitter makes it easier to get around this issue. plus, the twitter api does not allow posting the reason of reporting, unlike in the apps, they ask for reason for reporting. (someone may want to correct me on this)

# copyright
MIT License, do whatever you want with the script.

# contributions
yeah sure, go ahead.

# donations
BTC - bitcoin:bc1qc907ntl58ale0jy3am5z4cfsjx2qks8eqsqs4q
ETH - ethereum:0x03Fa9ce10EF29dd3ef9F7D00Ceee52613029993b
