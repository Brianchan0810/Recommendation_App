from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time
import pymysql

def request_with_retry(url, headers):
    try_nos = 0
    while try_nos < 3:
        try:
            source0 = requests.get(url, headers=headers, timeout=20)
            return source0

        except:
            try_nos += 1
            print('retry')
            time.sleep(20 * try_nos)

    raise ValueError('connection fail')

def insert_to_tb(df, table_name):
    con = pymysql.connect(host=host, user=username, passwd=pw, db=db_name)
    cursor = con.cursor()

    cursor.execute(f'delete from {table_name}')
    con.commit()

    column_list = ', '.join(list(df.columns.values))
    insert_nos = ('%s, ' * df.shape[1])[:-2]
    val_to_insert = df.values.tolist()

    for i, row in enumerate(val_to_insert):
        try:
            cursor.execute(f"insert into {table_name} ({column_list}) values ({insert_nos})", row)
            con.commit()
        except:
            print('row number: ' + str(i))

        if i != 0 and i % 20 == 0:
            print('inserted 20 more rows')

    con.close()
    return 'finished'

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
type_pattern = re.compile('(window|split)[\s-]?type', re.I)
hp_pattern = re.compile('([\d./]+)HP\s', re.I)

info_list = []
feature_list = []

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

            stock_status = ac_soup.find(attrs={"title": "Availability"}).text.strip().lower()

            ac_type = re.search(type_pattern, product_name).group(1).lower()

            horsepower = re.search(hp_pattern, product_name).group(1)

            broadway_code = info_table.find(attrs={"data-th": "Broadway Code"}).text.strip()

            brand_name = info_table.find(attrs={"data-th": "Brand"}).text.strip().lower()

            model_no = info_table.find(attrs={"data-th": "Model"}).text.strip()

            suggest_area = info_table.find(attrs={"data-th": area_pattern}).text.strip()
            if 'or below' in suggest_area:
                suggest_area_low_limit, suggest_area_up_limit = 0, suggest_area.split()[0]
            else:
                suggest_area_low_limit, suggest_area_up_limit = suggest_area.split('-')

            for item in ["Main Feature", "Main Feature 2", "Main Feature 3"]:
                try:
                    feature = info_table.find(attrs={"data-th": item}).text.strip().lower()
                    feature_list.append([ac_url, feature])
                except:
                    pass

            info_list.append([ac_url, stock_status, model_no, brand_name, ac_type, horsepower, price, broadway_code
                                    , suggest_area_low_limit, suggest_area_up_limit])
    except:
        print('page not found')

    counter += 1


host = '18.216.168.246'
username = 'user'
pw = 'user'
db_name = 'ac'

info_df = pd.DataFrame(info_list, columns=['url', 'stock_status', 'model_no', 'brand_name', 'ac_type', 'horsepower'
                                           , 'price', 'broadway_code', 'area_low_lim', 'area_up_lim'])
info_df['horsepower'] = info_df['horsepower'].apply(lambda x: x.replace('3/4', '0.75'))
info_df['horsepower'] = info_df['horsepower'].astype('float')
info_df[['price', 'area_low_lim', 'area_up_lim']] = info_df[['price', 'area_low_lim', 'area_up_lim']].astype('int')
insert_to_tb(info_df, 'info')
info_df.to_csv('info_backup.csv', index=False)

brand_df = pd.DataFrame({'brand_name': list(info_df['brand_name'].unique())})
insert_to_tb(brand_df, 'brand')
brand_df.to_csv('brand_backup.csv', index=False)

feature_df = pd.DataFrame(feature_list, columns=['url', 'feature'])
insert_to_tb(feature_df, 'feature')
info_df.to_csv('feature_backup.csv', index=False)
