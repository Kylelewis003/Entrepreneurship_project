from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask import Flask, request, jsonify, render_template
import requests
import pickle
import numpy as np
import pandas as pd
import os
from fertilizer import fertilizer_dic
from datetime import datetime, timedelta

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='harshithbhaskar'
API_KEY = 'b8e55cf2dbb376fce1e0b554aaa886e8'


model = pickle.load(open("model.pkl", "rb"))
with open('labels.pkl', 'rb') as f:
    labels = pickle.load(f)

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db_username = os.getenv('DB_USERNAME', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3307')  
db_name = os.getenv('DB_NAME', 'farmers')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
db = SQLAlchemy(app)

# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))

class Farming(db.Model):
    fid=db.Column(db.Integer,primary_key=True)
    farmingtype=db.Column(db.String(100))


class Addagroproducts(db.Model):
    username=db.Column(db.String(50))
    email=db.Column(db.String(50))
    pid=db.Column(db.Integer,primary_key=True)
    productname=db.Column(db.String(100))
    productdesc=db.Column(db.String(300))
    price=db.Column(db.Integer)



class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fid=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Register(db.Model):
    rid=db.Column(db.Integer,primary_key=True)
    farmername=db.Column(db.String(50))
    aadharnumber=db.Column(db.String(50))
    age=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    phonenumber=db.Column(db.String(50))
    address=db.Column(db.String(50))
    farming=db.Column(db.String(50))

    

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/farmerdetails')
@login_required
def farmerdetails():
    # query=db.engine.execute(f"SELECT * FROM `register`") 
    query=Register.query.all()
    return render_template('farmerdetails.html',query=query)

@app.route('/agroproducts')
@login_required
def agroproducts():
    # query=db.engine.execute(f"SELECT * FROM `addagroproducts`") 
    query=Addagroproducts.query.all()
    return render_template('agroproducts.html',query=query)

@app.route('/addagroproduct',methods=['POST','GET'])
@login_required
def addagroproduct():
    if request.method=="POST":
        username=request.form.get('username')
        email=request.form.get('email')
        productname=request.form.get('productname')
        productdesc=request.form.get('productdesc')
        price=request.form.get('price')
        products=Addagroproducts(username=username,email=email,productname=productname,productdesc=productdesc,price=price)
        db.session.add(products)
        db.session.commit()
        flash("Product Added","info")
        return redirect('/agroproducts')
   
    return render_template('addagroproducts.html')

@app.route('/triggers')
@login_required
def triggers():
    # query=db.engine.execute(f"SELECT * FROM `trig`") 
    query=Trig.query.all()
    return render_template('triggers.html',query=query)

@app.route('/addfarming',methods=['POST','GET'])
@login_required
def addfarming():
    if request.method=="POST":
        farmingtype=request.form.get('farming')
        query=Farming.query.filter_by(farmingtype=farmingtype).first()
        if query:
            flash("Farming Type Already Exist","warning")
            return redirect('/addfarming')
        dep=Farming(farmingtype=farmingtype)
        db.session.add(dep)
        db.session.commit()
        flash("Farming Addes","success")
    return render_template('farming.html')




@app.route("/delete/<string:rid>",methods=['POST','GET'])
@login_required
def delete(rid):
    # db.engine.execute(f"DELETE FROM `register` WHERE `register`.`rid`={rid}")
    post=Register.query.filter_by(rid=rid).first()
    db.session.delete(post)
    db.session.commit()
    flash("Slot Deleted Successful","warning")
    return redirect('/farmerdetails')


@app.route("/edit/<string:rid>",methods=['POST','GET'])
@login_required
def edit(rid):
    # farming=db.engine.execute("SELECT * FROM `farming`") 
    if request.method=="POST":
        farmername=request.form.get('farmername')
        aadharnumber=request.form.get('aadharnumber')
        age=request.form.get('age')
        gender=request.form.get('gender')
        phonenumber=request.form.get('phonenumber')
        address=request.form.get('address')
        farmingtype=request.form.get('farmingtype')     
        # query=db.engine.execute(f"UPDATE `register` SET `farmername`='{farmername}',`adharnumber`='{adharnumber}',`age`='{age}',`gender`='{gender}',`phonenumber`='{phonenumber}',`address`='{address}',`farming`='{farmingtype}'")
        post=Register.query.filter_by(rid=rid).first()
        print(post.farmername)
        post.farmername=farmername
        post.aadharnumber=aadharnumber
        post.age=age
        post.gender=gender
        post.phonenumber=phonenumber
        post.address=address
        post.farming=farmingtype
        db.session.commit()
        flash("Slot is Updates","success")
        return redirect('/farmerdetails')
    posts=Register.query.filter_by(rid=rid).first()
    farming=Farming.query.all()
    return render_template('edit.html',posts=posts,farming=farming)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        print(username,email,password)
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        # encpassword=generate_password_hash(password)

        # new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        newuser=User(username=username,email=email,password=password)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","warning")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/register',methods=['POST','GET'])
@login_required
def register():
    farming=Farming.query.all()
    if request.method=="POST":
        farmername=request.form.get('farmername')
        aadharnumber=request.form.get('aadharnumber')
        age=request.form.get('age')
        gender=request.form.get('gender')
        phonenumber=request.form.get('phonenumber')
        address=request.form.get('address')
        farmingtype=request.form.get('farmingtype')     
        query=Register(farmername=farmername,aadharnumber=aadharnumber,age=age,gender=gender,phonenumber=phonenumber,address=address,farming=farmingtype)
        db.session.add(query)
        db.session.commit()
        # query=db.engine.execute(f"INSERT INTO `register` (`farmername`,`adharnumber`,`age`,`gender`,`phonenumber`,`address`,`farming`) VALUES ('{farmername}','{adharnumber}','{age}','{gender}','{phonenumber}','{address}','{farmingtype}')")
        # flash("Your Record Has Been Saved","success")
        return redirect('/farmerdetails')
    return render_template('farmer.html',farming=farming)

@app.route('/crop', methods=['GET','POST'])
@login_required
def predict():
    if request.method == 'POST' : 
        try:
            temperature = request.form.get('temperature', '0')
            humidity = request.form.get('humidity', '0')
            ph = request.form.get('ph', '0')
            rainfall = request.form.get('rainfall', '0')
            try:
                float_features = [float(temperature), float(humidity), float(ph), float(rainfall)]
            except ValueError as ve:
                print(f"ValueError: {ve}") 
                flash("Invalid input data. Please ensure all fields are correctly filled.", "danger")
                return redirect(url_for('index'))
            features = [np.array(float_features)]
            probabilities = model.predict_proba(features)[0]
            crop_probabilities = list(zip(model.classes_, probabilities))
            crop_probabilities.sort(key=lambda x: x[1], reverse=True)
            top_3_crops = [crop_name for crop_name, _ in crop_probabilities[:3]]
            return render_template("crop_recommendation.html", 
                               prediction_text=f"The suitable crops for the land are {', '.join(top_3_crops)}")
        except Exception as e:
            print(f"Exception: {e}") 
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('index'))
    else:
        
        return render_template("crop_recommendation.html", prediction_text = '')
    
@app.route('/fertilizers', methods=['GET', 'POST'])
@login_required
def predict_fertilizer():
    if request.method == 'POST':
        crop_name = str(request.form['crop'])
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['potassium'])
        # ph = float(request.form['ph'])

        df = pd.read_csv(r"C:\Farm-erp\Farm-management-sysem-dbmsminiproject-main\farmer system\data\fertilizer.csv")

        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]

        n = nr - N
        p = pr - P
        k = kr - K
        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        max_value = temp[max(temp.keys())]
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
            else:
                key = "Nlow"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
            else:
                key = "Plow"
        else:  
            if k < 0:
                key = 'KHigh'
            else:
                key = "Klow"

        response = Markup(str(fertilizer_dic[key]))
        return render_template('Fertilizer_result.html', response = response)
    else:
        return render_template('Fertilizer_details.html')
    

@app.route('/weather', methods=['GET', 'POST'])
@login_required
def enterlocation():
    weather = None
    if request.method == 'POST':    
        location = request.form['location']
        weather = get_weather(location)
    return render_template('weather_forecast.html', weather=weather)

def get_weather(location):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['cod'] == 200:
            # Extract temperature, humidity, and rainfall
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            rain = data.get('rain', {}).get('1h', 0) 

            return {
                'city': data['name'],
                'temperature': main.get('temp'),
                'humidity': main.get('humidity'),
                'rainfall': rain,
                'description': weather.get('description'),
                'icon': weather.get('icon')
            }
    return None

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'
    
if __name__ == '__main__':
    app.run(debug=True)   
