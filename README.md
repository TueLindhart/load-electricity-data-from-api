# load-electricity-data-from-api 
Repo to load electricity data from https://api.eloverblik.dk/customerapi/index.html

## Setup

### Install necessary packages in a virtual environment:

#### With poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.in-project true
poetry install
source .venv/bin/activate
```

#### With python venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
```

## Usage

```bash
python electricity_api_loader/main.py
```

# Setup crontab

Create a .env with the following variables. 

```bash
GOOGLE_APPLICATION_CREDENTIALS='...'
TARGET_FOLDER_ID='...'
SHEET_ID='...'
FROM_EMAIL='...'
FROM_PASSWORD='...'
TO_EMAIL='...'
```

Create a output.log file
```bash
touch output.log
```

Create a cronjob to run every 10 minutes by `crontab -e` and insert

```bash
*/10 * * * * <path-to-repo>/load-electricity-data-from-api/init.sh >> <path-to-repo>/load-electricity-data-from-api/output.log 2>&1
```


