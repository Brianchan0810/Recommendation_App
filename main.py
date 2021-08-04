from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

url = 'https://www.broadwaylifestyle.com/hk_en/air-conditioner?p=product_list_order=general_categories'
source = requests.get('https://www.broadwaylifestyle.com/hk_en/air-conditioner?product_list_order=general_categories')

soup = BeautifulSoup(source.text,'html.parser')

total_nos = int(soup.select_one('p.toolbar-amount').text.strip().split('of')[-1].strip())

grid = soup.select_one("ol.products.list.items.product-items")
air_con = grid.select('li')
len(air_con)

air_con_link = []
for i in air_con:
    link = i.select_one('a')['href']
    air_con_link.append(link)

print(air_con_link)

page = 1
air_con_links = []
while True:
        print(f'now on page {page}')
        url = f'https://www.broadwaylifestyle.com/hk_en/air-conditioner?p={page}&product_list_order=general_categories'
        source = requests.get(url)
        soup = BeautifulSoup(source.text, 'html.parser')
        grid = soup.select_one("ol.products.list.items.product-items")
        air_con = grid.select('li')
        for i in air_con:
            link = i.select_one('a')['href']
            air_con_links.append(link)
            if len(air_con_links) >= 100:
                break
        if len(air_con_links) >= 100:
            break
        page +=1


print(air_con_links)
url1 = air_con_links[0]
source1 = requests.get(url1)
soup1 = BeautifulSoup(source1.text, 'html.parser')

status = soup.select_one('.product-info-stock-sku').text.strip()

name = soup1.select_one('.page-title').text.strip()
print(name)

find_hp = re.compile('([0-9.]+)\s?(?=HP)',re.I)
hp = find_hp.search(name).group(1)
print(hp)

find_type = re.compile('([a-zA-Z]+)[ -]?(?=type)',re.I)
ac_type = find_type.search('MS-22CRFB 2.5HP Inverter Split-type Air-conditioner').group(1)
print(ac_type)


price = soup.select_one('.normal-price span.price').text

cover_area = soup.select_one('tbody [data-th="Suggest Coverage area"]').text.split('-')
print(cover_area)

brand = soup.select_one('tbody [data-th="Brand"]').text

main_feature = []
feature1 = soup.select_one('tbody [data-th="Brand"]').text
main_feature.append(feature1)
feature_no =2
while True:
    try:
        feature = soup.select_one(f'tbody [data-th="Main Feature {feature_no}"]').text
        main_feature.append(feature)
        feature_no += 1
    except:
        break

air_con_dataset = []
ac_no = 1
for link in air_con_links:
    print(link)
    url = link
    source = requests.get(url)
    soup = BeautifulSoup(source.text, 'html.parser')

    status = soup.select_one('.product-info-stock-sku').text.strip()

    name = soup.select_one('.page-title').text.strip()
    print(name)

    try:
        find_hp = re.compile('([0-9./]+)\s?(?=HP)',re.I)
        hp = find_hp.search(name).group(1)
    except:
        hp = None

    try:
        find_type = re.compile('([a-zA-Z]+)[ -]?(?=Type)', re.I)
        ac_type = find_type.search(name).group(1)
        print(ac_type)
    except:
        ac_type = None

    price = soup.select_one('.normal-price span.price').text.split('$')[1].replace(',','')

    #cover_area = soup.select_one('tbody [data-th="Suggest Coverage area"]').text.split('-')
    #max_cover_area = cover_area[1]
    #min_cover_area = cover_area[0]

    brand = soup.select_one('tbody [data-th="Brand"]').text.strip()

    main_feature = []
    feature1 = soup.select_one('tbody [data-th="Main Feature"]').text
    main_feature.append(feature1)
    feature_no = 2
    while True:
        try:
            feature = soup.select_one(f'tbody [data-th="Main Feature {feature_no}"]').text
            main_feature.append(feature)
            feature_no += 1
        except:
            break
    air_con_dataset.append([name,status,hp,ac_type,price,brand,main_feature])
    print(f'AC no.{ac_no}')
    ac_no += 1


print(air_con_dataset)

df = pd.DataFrame(air_con_dataset, columns=['name','status','hp','ac_type','price','brand','main_feature'])
df['hp'].replace('3/4','0.75',inplace=True)
df.to_csv('air_con_db.csv')

df['ac_type'].shape[0]
df['price'] = df['price'].astype('float')

def test(df,type,brand,budget,hp):
    df['price'] = df['price'].astype('float')
    df['hp'] = df['hp'].astype('float')
    if df[df['brand']==brand].shape[0] == 0:
        message = 'No that brand'
        return message
    if df[df['type']==type].shape[0] == 0:
        message = 'No that type'
        return message
    filtered_df = df[(df['hp']==hp) & (df['ac_type']==type) & (df['brand']==brand) & (df['price']<budget)]
    brand_name = filtered_df['name'][0]
    price = filtered_df['price'][0]
    message = brand_name + ': price is HK$' + price
    return message

test(df,'Window','York',5000,1)
df['name']



