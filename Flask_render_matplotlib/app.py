from flask import Flask, render_template, request
import sqlite3
import json
import random

app = Flask(__name__)
@app.route("/test")
def test():

    return render_template('testing.html')


@app.route("/", methods=['GET','POST'])
def home():
    return render_template('home.html')
    if request.method == 'POST':
        return redirect('/graph')
    
    
@app.route("/data.json")
def data():
    connection = sqlite3.connect("data.sqlite")
    cursor = connection.cursor()
    cursor.execute("SELECT 1000*timestamp, measure from measures")
    results = cursor.fetchall()
    
    return json.dumps(results)

@app.route("/data_2.json")   #Peak-data
def data_2():
    connection2 = sqlite3.connect("peak_data.sqlite")
    cursor2 = connection2.cursor()
    cursor2.execute("SELECT 1000*timestamp, measure from measures")
    results2 = cursor2.fetchall()
    
    return json.dumps(results2)    
 
@app.route("/graph")
def graph():
    return render_template('graph.html')
 
 
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)