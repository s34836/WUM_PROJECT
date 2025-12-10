Data collection phase of data science project.
2-1.py - Gathering links to the cars listings.
2-2.py - Removing duplicate urls
2-3.py - Gathering JSONs of the cars listings.
2-4.py - Creating datadrame for future analysis.
2-5.py - Dlsplay script for one car listing.



# Data collection
python -m venv .venv
windows:
.venv\Scripts\activate
mac:
source ./.venv/bin/Activate
pip install --upgrade pip
pip install -r requirements.txt


or:
pyenv local 3.10.13
python -m venv .venv_tabtransformer
source .venv_tabtransformer/bin/activate