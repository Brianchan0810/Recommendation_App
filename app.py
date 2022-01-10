from flask import Flask, render_template, request
import logging #python building in package
import pandas as pd
from sqlalchemy import create_engine
import redis

#r = redis.Redis('18.216.168.246', port=6379, password='user')

app = Flask(__name__)

logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(name)s|%(message)s')
my_logger = logging.getLogger('brian')


@app.route('/', methods=['GET', 'POST'])
def query():
    #my_logger.warning('write log to bigquery')
    print(my_logger.name)
    if request.method == 'POST':
        ac_type = request.form.get('Air-Con Type')
        brand = request.form.get('Brand Name')
        budget = request.form.get('Budget')
        hp = request.form.get('Horse Power')

        if len(ac_type) + len(brand) + len(budget) + len(hp) == 0:
            return render_template('request_form.html', message='Please at least one criteria.', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if len(budget) > 0:
            try:
                budget = float(budget)
            except:
                return render_template('request_form.html', message='Detect invalid input.', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if len(hp) > 0:
            try:
                hp = float(hp)
            except:
                return render_template('request_form.html', message='Detect invalid input.', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        sql_engine = create_engine(f'mysql+pymysql://user:user@18.216.168.246/ac', pool_recycle=3600)
        db_connection = sql_engine.connect()
        df = pd.read_sql("select * from ac.ac_view", db_connection)

        if ac_type != '' and df[df['ac_type'] == ac_type].shape[0] == 0:
            return render_template('request_form.html', message='No that type', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if brand != '' and df[df['brand'] == brand].shape[0] == 0:
            return render_template('request_form.html', message='No that brand', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if len(request.form.get('Air-Con Type')) > 0:
            df = df[df['ac_type'] == ac_type]

        if len(request.form.get('Brand Name')) > 0:
            df = df[df['brand'] == brand]

        if len(request.form.get('Budget')) > 0:
            df = df[df['price'] < float(request.form.get('Budget'))]

        if len(request.form.get('Horse Power')) > 0:
            df = df[df['hp'] == float(request.form.get('Horse Power'))]

        if df.shape[0] == 0:
            return render_template('request_form.html', message='Sorry no match air-con', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        tables = df.reset_index(drop=True).iloc[0:3].to_dict('records')

        return render_template('request_form.html', message='', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp, tables=tables)

    return render_template('request_form.html', message='')
