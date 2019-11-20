from flask import Flask, jsonify, g
import os

app = Flask('media-api')
app.secret_key = os.environ.get(
    'SECRET_KEY', 'notreallyasecretbutsureyoudoyoudude'
)

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('DEBUG', True),
        port=os.environ.get('PORT', 8000)
    )
