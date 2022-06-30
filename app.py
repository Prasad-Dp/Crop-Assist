# Importing essential libraries and modules

from msilib.schema import tables
import re
from flask import Flask, render_template, request, Markup,Response
import numpy as np
import pickle
import mysql.connector
import datetime
from gtts import gTTS
import pandas as pd
from utils.fertilizer import fertilizer_dic
from csv import writer
# ==============================================================================================
user_name = ""
ec = ""
city = ""
state = ""
pincode = 0
area = ""
audio_name=""
# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------
 
# Loading crop recommendation model

crop_recommendation_model_path = 'models/crop_rec.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

# =========================================================================================

# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)


# render home page


@app.route('/')
def home():
    return render_template('index.html')


# render crop recommendation form page
@app.route('/user-log')
def user_log():
    return render_template('login.html')

@app.route('/user-info')
def user_info():
    return render_template('user_details.html')


@app.route('/user-reg')
def user_reg():
    return render_template('regist.html')

@app.route('/user_registration', methods=['POST'])
def user_registration():
    if request.method == 'POST':
        r_name = request.form['r_name']
        eemail= request.form['eemail']
        mobile =request.form['mobile']
        u_name = request.form['u_name']
        passw = request.form['pass']

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="249209", database="cropdb")
        mycursor = mydb.cursor()
        c=[]
        c.append(u_name)
        d=[]
        d.append(eemail)
        sqln="select u_name from reg where u_name=(%s)"
        mycursor.execute(sqln,c)
        u_n=mycursor.fetchone();
        sqlp="select email from reg where email=(%s)"
        mycursor.execute(sqlp,d)
        u_m=mycursor.fetchone();
        if u_n!=None:
            error = "User Name already exists"
            return render_template('regist.html',error=error)
        elif u_m!=None:
            error = "Email already exists"
            return render_template('regist.html',error=error)
        else:
            sqlform = "insert into reg values(%s,%s,%s,%s,%s)"
            test_d = (r_name,eemail,mobile,u_name,passw)
            mycursor.execute(sqlform, test_d)
            mydb.commit()

            return render_template('login.html')

@app.route('/user_check', methods=['POST'])
def user_check():
    if request.method == 'POST':
        u_name =request.form['u_name']
        passw = request.form['pass']

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="249209", database="cropdb")
        mycursor = mydb.cursor()
        c=[]
        c.append(u_name)
        d=[]
        d.append(passw)
        sqln="select u_name from reg where u_name=(%s)"
        sqlp="select pass from reg where u_name=(%s)"
        mycursor.execute(sqln,c)
        u_n=mycursor.fetchone();

        mycursor.execute(sqlp,d)
        u_p=mycursor.fetchone();

        if(u_n==None):
            error = "invalid username"
            return render_template('login.html',error=error)
        elif(u_p==None):
            error = "invalid username"
            return render_template('login.html',error=error)
        else:
            sqlun="select name from reg where u_name=(%s)"
            mycursor.execute(sqlun,c)
            name_user=mycursor.fetchone();
            final_name=str(name_user[0])
            return render_template('home.html',final_name_u=final_name)


@app.route('/user-data', methods=['POST'])
def user_data():
    if request.method == 'POST':
        global user_name, ec, city, state, pincode, area
        user_name = request.form['name']
        ec = request.form['ec']
        area = request.form['area']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        return render_template('input.html')



@app.route('/fetrilizer')
def fetrilizer():
    return render_template('fetlizer.html')

@app.route('/fet-rec', methods=['POST'])
def fet_rec():
    if request.method == 'POST':
        Nit =int( request.form['nitrogen'])
        Pho = int(request.form['phosphorous'])
        pot = int (request.form['potassium'])
        crop = request.form['crop']
        print(type(crop))
        df = pd.read_csv('utils/fertilizer.csv')

        nr = df[df['Crop'] == crop]['N'].iloc[0]
        pr = df[df['Crop'] == crop]['P'].iloc[0]
        kr = df[df['Crop'] == crop]['K'].iloc[0]

        n = nr - Nit
        p = pr - Pho
        k = kr - pot
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

        return render_template('fet_result.html',fetrilizer=response)
      

@app.route('/alg-analysis')
def alg_analysis():
    cdf = pd.read_csv("utils\data.csv")
    sumer_crops=(cdf[(cdf['temperature'] > 30) & (cdf['humidity'] > 50)]['label'].unique())
    winter_crops=(cdf[(cdf['temperature'] < 20) & (cdf['humidity'] > 30)]['label'].unique())
    print(cdf[(cdf['rainfall'] > 200) & (cdf['humidity'] > 30)]['label'].unique())

    return render_template('alg_analysis.html',summer_crop=sumer_crops,winter_crop=winter_crops)

@app.route('/')
def logout():
    return render_template('index.html')

@app.route('/user-check')
def main_home():
    return render_template('home.html')

@app.route('/admin-login')
def admin_login():
    return render_template('admin.html')

@app.route('/admin_check', methods=['POST'])
def admin_check():
    if request.method == 'POST':
        u_name =request.form['a_name']
        passw = request.form['a_pass']
        if(u_name=="root" and passw=="249209"):
            data_users=pd.read_csv('static/output/data.csv')
            return render_template('data.html',tables=[data_users.to_html()],titles=[''])
        else:
            error = "invalid credentials"
            return render_template('admin.html',error=error)

@app.route('/model-report')
def model_report():
    return render_template('model_report.html')


@app.route('/random-forest')
def random_forest():
    return render_template('rf.html')


@app.route('/decesion-tree')
def deceision_tree():
    return render_template('dt.html')

@app.route('/svm')
def svm():
    return render_template('svm.html')
# ===============================================================================================


# render crop recommendation result page


@app.route('/crop_prediction', methods=['POST'])
def crop_prediction():
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['potassium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        temp = float(request.form['temperature'])
        hum = float(request.form['humidity'])
        data = np.array([[N, P, K, temp, hum, ph, rainfall]])
        my_prediction = crop_recommendation_model.predict(data)
        final_prediction = my_prediction[0]

        now = datetime.datetime.now()
        time_s=now.strftime("%Y-%m-%d %H:%M")

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="249209", database="cropdb")
        mycursor = mydb.cursor()
        sqlform = "insert into crop_data values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        test_d = (N, P, K, temp, hum, ph, rainfall, final_prediction, ec, user_name, area, city, state, pincode,time_s)
        mycursor.execute(sqlform, test_d)
        mydb.commit()

        cs_d = (N, P, K, temp, hum, ph, rainfall, final_prediction, ec, user_name, area, city, state, pincode,time_s)
        with open('static/output/data.csv', 'a+',newline="") as f:
            append_writer = writer(f)
            append_writer.writerow(cs_d)
            f.close()

        naa=["asAccc"]
        sqld="select user_name from crop_data where user_name=(%s)"

        mycursor.execute(sqld,naa)
        res=mycursor.fetchone();
        print(res)

        
        language = 'en'
        myobj = gTTS(text=final_prediction, lang=language, slow=False)
        myobj.save("audios/crop.mp3")

        df = pd.read_csv('utils/fertilizer.csv')

        nr = df[df['Crop'] == final_prediction]['N'].iloc[0]
        pr = df[df['Crop'] == final_prediction]['P'].iloc[0]
        kr = df[df['Crop'] == final_prediction]['K'].iloc[0]

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
        global audio_name
        audio_name=key

        return render_template('result.html', prediction=final_prediction,fetrilizer=response)

@app.route("/crop_audio")
def streamwav():
    def generate():
        with open("audios/crop.mp3", "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/x-mp3")

@app.route("/fetrilizer_audio")
def streamwav1():
    def generate():
        file_name=""
        if(audio_name=='NHigh'):
            file_name="audios/NHigh.mp3"
        elif(audio_name=="Nlow"):
            file_name="audios/NLow.mp3"
        elif(audio_name=='PHigh'):
            file_name="audios/PHigh.mp3"
        elif(audio_name=="Plow"):
            file_name="audios/PLow.mp3"
        elif(audio_name=='KHigh'):
            file_name="audios/KHigh.mp3"
        elif(audio_name=="KLow"):
            file_name="audios/Klow.mp3"
        else:
            file_name="audios/crop.mp3"
        print(file_name)
        with open(file_name, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/x-mp3")

# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=True)
