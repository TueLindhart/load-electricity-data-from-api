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

export GOOGLE_APPLICATION_CREDENTIALS="..."
export TARGET_FOLDER_ID="..."
```

## Usage

```bash
python electricity_api_loader/main.py
```

