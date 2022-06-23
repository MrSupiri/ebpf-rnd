import json
from flask import Flask
import os
import requests

app = Flask(__name__)
print("PID:", os.getpid())

@app.route('/http')
def http():
    r = requests.get("http://postman-echo.com/get?foo1=bar1&foo2=bar2")
    print("Resp:", r.json())
    return ('', 200) 

@app.route('/https')
def https():
    r = requests.get("https://postman-echo.com/get?foo1=bar1&foo2=bar2")
    print("Resp:", r.json())
    return ('', 200) 

@app.route('/empty')
def empty():
    return ('', 200) 


app.run(port=9094)