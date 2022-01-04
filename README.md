```
git clone https://github.com/feifeibear/tomtomzhua.git 
pip install -r requirements.txt

# Scraping from TOMTOM website the 'daily congestion index' for cities 
python tomtom_scraper.py

# Calculate country-level monthly averaged congestion index based on city-level daily congestion index
python tomtom_ratio_calc.py
```
