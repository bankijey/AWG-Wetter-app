from flask import Flask
import main
from urllib.parse import urlparse

app = Flask(__name__)

ENV = 'DEV'

@app.route('/')
def hello_world():
    return 'Hello World!'

def main():
    return main()

if __name__ == '__main__':
    app.run()
