from flask import Flask
from config import app
from routes.product_routes import product_bp
from routes.category_routes import category_bp


# Registrar las rutas
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(category_bp, url_prefix='/api/categories')


if __name__ == '__main__':
    app.run(debug=True)
