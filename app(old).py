from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd

class queryform(FlaskForm):
    ac_type = StringField('ac_type',validators=[DataRequired()])
    brand = StringField('brand', validators=[DataRequired()])
    budget = StringField('budget', validators=[DataRequired()])
    hp = StringField('hp', validators=[DataRequired()])
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FUCKME'

@app.route('/',methods=['GET','POST'])
def query():
    form = queryform()
    if form.validate_on_submit():
        request_type = form.ac_type.data
        request_brand = form.brand.data
        request_budget = float(form.budget.data)
        request_hp = float(form.hp.data)
        df = pd.read_csv('air_con_db.csv')
        df['price'] = df['price'].astype('float')
        df['hp'] = df['hp'].astype('float')
        if df[df['brand']==request_brand].shape[0] == 0:
            message = 'No that brand'
            return render_template('form.html', form=form, message=message)
        if df[df['ac_type']==request_type].shape[0] == 0:
            message = 'No that type'
            return render_template('form.html', form=form, message=message)
        filtered_df = df[(df['hp']==request_hp) & (df['ac_type']==request_type) & (df['brand']==request_brand) & (df['price']<request_budget)].sort_values(by='price',ascending=True)
        best_name = filtered_df['name'].iloc[0]
        best_price = filtered_df['price'].iloc[0]
        message = str(best_name) + ': price is HKD ' + str(best_price)
        return render_template('form2.html',form=form,message=message)
    return render_template('form2.html',form=form,message='')
