from flask import Flask, render_template, request
import logging #python building in package
import pandas as pd
import redis
import pymysql

r = redis.Redis('my-redis', decode_responses=True)

app = Flask(__name__)

host = '18.216.168.246'
username = 'user'
pw = 'user'
db_name = 'ac'

#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(name)s|%(message)s')
#my_logger = logging.getLogger('brian')


@app.route('/', methods=['GET', 'POST'])
def ac_query():
    if len(r.lrange('brand_list', 0, -1)) == 0:
        con = pymysql.connect(host=host, user=username, passwd=pw, db=db_name)
        cursor = con.cursor()

        cursor.execute('select * from brand')
        result = cursor.fetchall()
        brand_list = ['All'] + [item for row in result for item in row]

        con.close()

        r.rpush('brand_list', *brand_list)
        r.expire('brand_list', 60*60*24)
    else:
        brand_list = r.lrange('brand_list', 0, -1)

    #my_logger.warning('write log to bigquery')
    #print(my_logger.name)
    if request.method == 'POST':
        ac_type = request.form.get('ac_type')
        brand_name = request.form.get('brand_name')
        budget = request.form.get('budget')
        hp = request.form.get('hp')

        if len(budget) > 0:
            try:
                budget = float(budget)
            except:
                return render_template('request_form.html', message='Detect invalid input.')

        criteria_key = f'ac_type={ac_type}+brand_name={brand_name}+budget={budget}+hp={hp}'

        if r.get(criteria_key) == None:
            filter_statement = ["stock_status = 'in stock'"]

            if ac_type != 'All':
                filter_statement.append(f"ac_type = '{ac_type}'")

            if brand_name != 'All':
                filter_statement.append(f"brand_name = '{brand_name}'")

            if budget != '':
                filter_statement.append(f"price < {budget}")

            if hp != 'All':
                if hp == '3/4':
                    filter_statement.append('horsepower = 0.75')
                else:
                    filter_statement.append(f"horsepower = '{float(hp)}'")

            query = 'select broadway_code, brand_name, ac_type, price, url from info where ' \
                    + ' and '.join(filter_statement) + ' order by price desc limit 3'

            con = pymysql.connect(host=host, user=username, passwd=pw, db=db_name)
            cursor = con.cursor()

            cursor.execute(query)
            result = cursor.fetchall()
            con.close()

            df = pd.DataFrame(result, columns=['broadway_code', 'brand_name', 'ac_type', 'price', 'url'])

            if df.shape[0] == 0:
                return render_template('request_form.html', message='Sorry no match air-con')

            suggestions = df.to_dict('records')

            r.set(criteria_key, render_template('request_form.html', brand_list=brand_list, suggestions=suggestions))
            r.expire(criteria_key, 60*60*24*5)

        return r.get(criteria_key)

    return render_template('request_form.html', brand_list=brand_list)
