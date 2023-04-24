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
        -n,     --negative-filter       specify one optional negative filter.
        -p,     --positive-filter       specify one optional positive filter.
        -o,     --active_search         True or False: if activated, OPP will trigger osint techniques
        -k,     --api_key               to be furnished by the user, if not will scrap
        -c,     --cse_id                to be furnished by the user, if not will scrap
```