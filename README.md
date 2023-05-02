# Online Privacy Pilot

The OnlinePrivacyPilot software is designed to evaluate and manage the online traces of a user by identifying and categorizing footprints left on the internet. The footprints, which collectively form the user's online fingerprint, can include search results, social media accounts, website registrations, comments, posts, images, and more. The tool aims to be a companion for responsible online data management, providing solutions for removing personal information from identified sources.

## Installation

Clone the repository :
```
git clone git@github.com:OnlinePrivacyPilot/OnlinePrivacyPilot.git
```

Create a Python virtualenv :
```
cd OnlinePrivacyPilot
virtualenv .venv
. ./.venv/bin/activate 
```

Install the Python package :
```
pip install -e .
```

## CLI

### Search API Key

As the software uses Google Custom Search API, it's necessary to obtain API key and a CSE id.
To do so you should pass it as an option of the entry command, this could be for instance:
```
oppcli -d 2 -o -k "key_from_user" -c "cse_id_user" "target_user"
```
The `-k` option is used to specify the API where the `-c` is linked to the CSE id.

### Help
```
oppcli -h               
```
```
Usage: oppcli [OPTIONS] <target>

General:
        -h,     --help                  print this help.
        -d,     --depth                 specify the maximum depth of the search.
        -n,     --negative-filter       specify optional negative filter.
        -p,     --positive-filter       specify optional positive filter.
        -o,     --active_search         activate OSINT techniques in the research process
        -q,     --quiet                 disable the display of the ascii tree in output
        -s,     --store                 store obtained fingerprint as : none (default), db (SQLITE file only), dot (SQLITE file + DOT file + PNG)
        -k,     --api_key               specify Google search API Key, if empty, the program will get results using a scrapping library
        -c,     --cse_id                specify Custom Search Engine ID, if empty, the program will get results using a scrapping library
```