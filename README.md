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

As the software uses Google Custom Search API, it's necessary to obtain API key, and put it in the `src/credentials.py` like this :
```py
API_KEY = "YOUR_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"
```

### Help
```
oppcli -h               
```
```
Usage: oppcli [OPTIONS] <target>

General:
	-h,	--help			print this help.
	-d,	--depth			specify the maximun depth of the search.
```