import configparser
import os
import shutil
import logging
import argparse
import tools
import donwloader
from datetime import *

# Set logging params
log_file = 'gibdd_rta_data_extractor'
try:
    os.remove(f'{log_file}.log')
except:
    pass
logging.basicConfig(
    handlers=[
        logging.FileHandler(f'{log_file}.log'),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format='%(levelname)s %(message)s')

# Get config file
config = configparser.ConfigParser()
config.read('settings.cfg')

# Get args
parser = argparse.ArgumentParser("gibdd_rta_data_extractor")
parser.add_argument("--start_date", help="Format mm.yyyy", type=tools.valid_date)
parser.add_argument("--end_date", help="Format mm.yyyy", type=tools.valid_date)
args = parser.parse_args()

start_date = args.start_date if args.start_date != None else datetime.strptime('01.2020', '%m.%Y')
end_date = args.end_date if args.end_date != None else datetime.strptime('01.2020', '%m.%Y')

# Get packs of RTA cards
formats = ['XML', 'XLS']

try:
    shutil.rmtree('cards')
except:
    pass

dwl = donwloader.Downloader(config=config)

for format in formats:
    dwl.download_packs(start_date, end_date, format)