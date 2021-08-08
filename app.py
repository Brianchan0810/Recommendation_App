from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def query():
    if request.method == 'POST':
        ac_type = request.form.get('Air-Con Type')
        brand = request.form.get('Brand Name')
        budget = request.form.get('Budget')
        hp = request.form.get('Horse Power')

        if len(ac_type) == 0 and len(brand) == 0 and len(budget) == 0 and len(hp) == 0:
            return render_template('request_form.html', message='Please at least one criteria.', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if len(budget)>0:
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

        df = pd.read_csv('air_con_db.csv')
        df['price'] = df['price'].astype('float')
        df['hp'] = df['hp'].astype('float')

        if df[df['ac_type'] == ac_type].shape[0] == 0:
            return render_template('request_form.html', message='No that type', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if df[df['brand'] == brand].shape[0] == 0:
            return render_template('request_form.html', message='No that brand', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        if len(request.form.get('Air-Con Type'))>0:
            df = df[df['ac_type'] == ac_type]

        if len(request.form.get('Brand Name'))>0:
            df = df[df['brand'] == brand]

        if len(request.form.get('Budget')) > 0:
            df = df[df['price']<float(request.form.get('Budget'))]

        if len(request.form.get('Horse Power')) > 0:
            df = df[df['hp'] == float(request.form.get('Horse Power'))]

        if df.shape[0] == 0:
            return render_template('request_form.html', message='Sorry no match air-con', ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

        message = {'result': df.reset_index(drop=True).iloc[0:3].T.to_dict()}

        return render_template('request_form.html',message=message, ac_type=ac_type,
                                   brand=brand, budget=budget, hp=hp)

    return render_template('request_form.html',message='')
