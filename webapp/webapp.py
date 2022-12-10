from flask import Flask
from threading import Thread
from views import views

# WEBAPP VERSION = 1.0w

app = Flask('')
app.register_blueprint(views, url_prefix="/")


def run():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    Thread(target=run).start()  # Start the flask webpage
