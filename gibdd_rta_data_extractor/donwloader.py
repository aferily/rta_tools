import requests
import os
import zipfile
import logging
import tools
from datetime import *

class Downloader:
    def __init__(self, config) -> None:
        self.config = config
        
    def __download_pack_by_id(self, pack_id: int) -> bool:
        'Download pack of RTA cards by ID.'

        logging.info(f'Pack downloading: {self.start_date.strftime('%d.%m.%Y')} '
                     f'- {self.end_date.strftime('%d.%m.%Y')}. Format: {self.format}.')

        output_folder = f'cards/{self.format}'

        try:
            url_rta_cards_donwload = self.config['stat_gibdd']['download']
        except:
            logging.error('Invalid configuration file. Set pack downloading URL.')
            return False
        
        url_rta_cards_donwload += f'?data={pack_id}'

        try:
            response = requests.get(url_rta_cards_donwload)
        except:
            logging.exception(f'Pack downloading failed. Network error.')
            return False
        
        if response.status_code != 200:
            logging.error(f'Pack downloading request is not completed.'
                          f'Status code: {response.status_code}.')
            return False

        tmp_zip_file = 'tmp.zip'    
        with open(tmp_zip_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk: 
                    f.write(chunk)

        os.makedirs(output_folder, exist_ok=True)
        with zipfile.ZipFile(tmp_zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            counter = 1
            for file_name in file_list:
                temp_file_path = zip_ref.extract(file_name, output_folder)
                
                new_file_name = f'{self.start_date.strftime('%d%m%Y')}_{self.end_date.strftime('%d%m%Y')}' \
                                f'_{pack_id}_{counter}{os.path.splitext(file_name)[1]}'
                new_file_path = os.path.join(output_folder, new_file_name)

                os.rename(temp_file_path, new_file_path)
                
                counter += 1

        try:
            os.remove(tmp_zip_file)
        except:
            pass

        logging.info(f'Pack downloaded!')
        return True

    def __generate_pack_by_period(self) -> list[str]:
        'Generate pack of RTA cards for the specified period in the specified format.'

        logging.info(f'Pack generation: {self.start_date.strftime('%d.%m.%Y')} - '
                     f'{self.end_date.strftime('%d.%m.%Y')}. Format: {format}.')

        try:
            generate_methods = {
                'XML': self.config['stat_gibdd']['generate_xml'], 
                'XLS': self.config['stat_gibdd']['generate_xls']
            }
        except:
            logging.error('Invalid configuration file. Set pack generation URLs.')
            return
        
        if not self.format in generate_methods:
            logging.error(f'Pack format {self.format} is not supported. '
                          f'Available formats {list(generate_methods.keys())}.')
            return
        url_rta_cards_generate = generate_methods[self.format]

        request_data = f'{{"data":"{{\
        \\"date_st\\":\\"{self.start_date.strftime('%d.%m.%Y')}\\",\
        \\"date_end\\":\\"{self.end_date.strftime('%d.%m.%Y')}\\",\
        \\"ParReg\\":\\"877\\",\
        \\"order\\":{{\\"type\\":1,\\"fieldName\\":\\"dat\\"}},\
        \\"reg\\":[\\"40\\"],\
        \\"ind\\":\\"161\\",\
        \\"exportType\\":1}}"}}'

        try:
            response = requests.post(
                url_rta_cards_generate, 
                data=request_data, 
                headers={'content-type': 'application/json'})
        except:
            logging.exception(f'Pack generation failed. Network error.')
            return

        if response.status_code != 200:
            logging.error(f'Pack generation request is not completed.'
                          f'Status code: {response.status_code}.')
            return
        
        content = response.json()
        resp_data = content.get('data')
        if resp_data == None:
            logging.error(f'Incorrect response to the pack generation request: {content}.')
            return

        pack_ids = resp_data.split(';')
        logging.info(f'Pack generated! id: {pack_ids}.')

        return pack_ids
    
    def download_packs(self, start_date: date, end_date: date, format: str):
        'Generate and download packs of RTA cards.'
        self.format = format

        periods = tools.split_period_by_month(start_date, end_date)
        for period in periods:
            self.start_date = period[0]
            self.end_date = period[1]

            pack_ids = self.__generate_pack_by_period()
            
            if pack_ids == None:
                return
            
            for pack_id in pack_ids:
                if not self.__download_pack_by_id(pack_id):
                    return