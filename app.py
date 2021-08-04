from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def query():
    if request.method == 'POST':
        request_type = request.form.get('Air-Conditioner Type')
        request_brand = request.form.get('Brand Name')
        if len(request.form.get('Budget')) > 0:
            client_budget = float(request.form.get('Budget'))
        if len(request.form.get('Horse Power')) > 0:
            request_hp = float(request.form.get('Horse Power'))

        if len(request_type) == 0 and len(request_brand) == 0 and len(client_budget) == 0 and len(request_hp) == 0:
            return render_template('form2.html', message='Please at least provide one criteria.')

        df = pd.read_csv('air_con_db.csv')
        df['price'] = df['price'].astype('float')
        df['hp'] = df['hp'].astype('float')

        if df[df['brand']==brand].shape[0] == 0:
            return render_template('form2.html', message='No that brand')
        if df[df['ac_type']==ac_type].shape[0] == 0:
            return render_template('form2.html', message='No that type')

        return render_template('form2.html',message='success')

    return render_template('form2.html',message='')
