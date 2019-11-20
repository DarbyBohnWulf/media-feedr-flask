from flask import Flask, jsonify, g
import os
import models

app = Flask('media-api')
app.secret_key = os.environ.get(
    'SECRET_KEY', 'notreallyasecretbutsureyoudoyoudude'
)


@app.before_request
def before_request():
    print("connected to db")
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(res):
    print("disconnected from db")
    g.db.close()
    return res


if __name__ == '__main__':
    models.initialize()
    app.run(
        debug=os.environ.get('DEBUG', True),
        port=os.environ.get('PORT', 8000)
    )
