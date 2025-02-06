from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Ko than myint tun, hope you are doing well and welcome to our Channel Web Site!!!'
