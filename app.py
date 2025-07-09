from flask import Flask
from config import app


# Registrar las rutas


@app.route('/')
def home():
    return 'Hello, World !'

if __name__ == '__main__':
    app.run(debug=True)
