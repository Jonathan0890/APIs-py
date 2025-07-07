from flask import Flask
from config import app
from extenciones import bcrypt, jwt
from routes.product_routes import product_bp
from routes.category_routes import category_bp
from routes.product_category_routes import product_category_bp
from routes.pedido_routes import pedido_bp
from routes.detalle_pedido_routes import detalle_bp
from routes.user_routes import user_bp
from routes.pago_routes import pago_bp
from routes.resena_routes import resena_bp
from routes.direccion_routes import direccion_bp
from routes.carrito_routes import carrito_bp
from routes.cupones_routes import cupon_bp
from routes.auth_routes import auth_bp


# Registrar las rutas
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(category_bp, url_prefix='/api/categories')
app.register_blueprint(product_category_bp, url_prefix='/api/products_categories')
app.register_blueprint(pedido_bp, url_prefix='/api/pedidos')
app.register_blueprint(detalle_bp, url_prefix='/api/detalles_pedidos')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(pago_bp, url_prefix='/api/pagos')
app.register_blueprint(resena_bp, url_prefix='/api/resenas')
app.register_blueprint(direccion_bp, url_prefix='/api/direcciones')
app.register_blueprint(carrito_bp, url_prefix='/api/carritos')
app.register_blueprint(cupon_bp, url_prefix='/api/cupones')


# Inicializa las extensiones con la app
bcrypt.init_app(app)
jwt.init_app(app)

@app.route('/')
def home():
    return 'Hello, World !'

if __name__ == '__main__':
    app.run(debug=True)
