from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
import time
from sqlalchemy import create_engine
import pymysql

def request_with_retry(url, headers):
    try_nos = 1
    while try_nos < 3:
        try:
            source0 = requests.get(url, headers=headers, timeout=20)
            return source0
        except:
            print('retry')
            time.sleep(20 * try_nos)
            try_nos += 1
    raise ValueError('connection fail')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}

url = 'https://www.broadwaylifestyle.com/hk_en/air-conditioner?p=1&product_list_dir=desc'
source = request_with_retry(url, headers)
soup = BeautifulSoup(source.text, 'html.parser')
total_nos = int(soup.select_one('p.toolbar-amount').text.strip().split(' of ')[1])


# get all individual air-conditioner url
url_list = []
page_no = 1
while len(url_list) < total_nos:
    print(f'now on page{page_no}')

    page_url = f'https://www.broadwaylifestyle.com/hk_en/air-conditioner?p={page_no}&product_list_dir=desc'
    page_source = request_with_retry(page_url, headers)
    page_soup = BeautifulSoup(page_source.text, 'html.parser')

    blocks = page_soup.select('li.item.product.product-item')
    for block in blocks:
        url_list.append(block.select_one('div.product-item-info a')['href'])

    page_no += 1


# get individual air-conditioner information
area_pattern = re.compile('Coverage Area', re.I)
type_pattern = re.compile('(\w+)[\s-]?type', re.I)
hp_pattern = re.compile('([\d./]+)HP\s', re.I)

total_info_list = []

counter = 0
for ac_url in url_list[counter:]:
    print(f'aircon number: {counter}')

    ac_source = request_with_retry(ac_url, headers)
    ac_soup = BeautifulSoup(ac_source.text, 'html.parser')

    info_table = ac_soup.select_one('table', id='product-attribute-specs-table')

    try:
        product_name = info_table.find(attrs={"data-th": "Product Name"}).text.strip()

        if re.search(type_pattern, product_name): # exclude potable or unknown type aircon
            price = ac_soup.select_one('div.price').text.strip().split('$')[1].replace(',', '')

            ac_type = re.search(type_pattern, product_name).group(1).lower()

            horsepower = re.search(hp_pattern, product_name).group(1)

            broadway_code = info_table.find(attrs={"data-th": "Broadway Code"}).text.strip()

            brand_name = info_table.find(attrs={"data-th": "Brand"}).text.strip()

            model_no = info_table.find(attrs={"data-th": "Model"}).text.strip()

            feature1 = info_table.find(attrs={"data-th": "Main Feature"}).text.strip()

            try:
                feature2 = info_table.find(attrs={"data-th": "Main Feature 2"}).text.strip()
            except:
                feature2 = None

            try:
                feature3 = info_table.find(attrs={"data-th": "Main Feature 3"}).text.strip()
            except:
                feature3 = None

            suggest_area = info_table.find(attrs={"data-th": area_pattern}).text.strip()
            print(suggest_area)
            if 'or below' in suggest_area:
                suggest_area_low_limit, suggest_area_up_limit = 0, suggest_area.split()[0]
            else:
                suggest_area_low_limit, suggest_area_up_limit = suggest_area.split('-')

            total_info_list.append([ac_url, model_no, brand_name, ac_type, horsepower, price, broadway_code
                                    , suggest_area_low_limit, suggest_area_up_limit, feature1, feature2, feature3])
    except:
        print('page not found')

    counter += 1

len(url_list)

info_df = pd.DataFrame(total_info_list, columns=['url', 'model_no', 'brand_name', 'ac_type', 'horsepower', 'price'
                                                 , 'broadway_code', 'suggest_area_low_limit', 'suggest_area_up_limit'
                                                 , 'feature1', 'feature2', 'feature3'])

info_df['horsepower'] = info_df['horsepower'].apply(lambda x: x.replace('3/4', '0.75'))
info_df['horsepower'] = info_df['horsepower'].astype('float')
info_df[['price', 'suggest_area_low_limit', 'suggest_area_up_limit']] = \
    info_df[['price', 'suggest_area_low_limit', 'suggest_area_up_limit']].astype('int')

info_df.to_csv('new_info.csv', index=False)
info_df = pd.read_csv('new_info.csv')
info_df.rename(columns={'suggest_area_low_limit': 'area_low_lim', 'suggest_area_up_limit': 'area_up_lim'}, inplace=True)
test = pd.DataFrame({'url':['a', 'b'], 'model_no': ['aaa', 'bbb'], 'brand_name': ['aaa', 'bbb'], 'ac_type': ['aaa', 'bbb']
                    , 'horsepower': [1, 2], 'price': [300, 100], 'broadway_code': ['aaa', 'bbb']
                    , 'suggest_area_low_limit': [10, 30], 'suggest_area_up_limit': [20, 40]
                    , 'feature1': ['aaa', 'bbb'], 'feature2': ['aaa', 'bbb'], 'feature3': ['aaa', 'bbb']})

new_df = pd.read_csv('new_info.csv')
new_df
info_df1 = info_df.iloc[:21]
info_df2 = info_df.iloc[21:51]
info_df3 = info_df.iloc[51:101]
info_df4 = info_df.iloc[101:131]
info_df5 = info_df.iloc[131:141]
info_df6 = info_df.iloc[141:145]
info_df7 = info_df.iloc[145:146]
info_df.iloc[146]
info_df8 = info_df.iloc[146:148]
sql_engine = create_engine(f'mysql+pymysql://user:user@18.216.168.246/ac', pool_recycle=3600)
db_connection = sql_engine.connect()
info_df8.to_sql('info', db_connection, if_exists='append', index=False)
db_connection.close()

total_status_list = []

counter = 0
for ac_url in url_list[counter:]:
    print(f'aircon number: {counter}')

    ac_source = request_with_retry(ac_url, headers)
    ac_soup = BeautifulSoup(ac_source.text, 'html.parser')

    info_table = ac_soup.select_one('table', id='product-attribute-specs-table')

    try:
        product_name = info_table.find(attrs={"data-th": "Product Name"}).text.strip()

        if re.search(type_pattern, product_name): # exclude potable or unknown type aircon
            status = ac_soup.find(attrs={"title": "Availability"}).text.strip()
            print(status)

            total_status_list.append([ac_url, status])
    except:
        print('page not found')

    counter += 1

status_df = pd.DataFrame(total_status_list, columns=['url', 'stock_status'])
status_df.to_csv('new_status.csv', index=False)

sql_engine = create_engine(f'mysql+pymysql://user:user@18.216.168.246/ac', pool_recycle=3600)
db_connection = sql_engine.connect()
status_df.to_sql('stock', db_connection, if_exists='append', index=False)
db_connection.close()


