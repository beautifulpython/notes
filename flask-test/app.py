from flask import Flask
from hello import hello_blueprint

app = Flask(__name__)

app.register_blueprint(hello_blueprint, url_prefix="/v1/hello")


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
