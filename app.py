from flask import Flask
from config import app
from routes.product_routes import product_bp
from routes.category_routes import category_bp
from routes.product_category_routes import product_category_bp
from routes.pedido_routes import pedido_bp
from routes.detalle_pedido_routes import detalle_bp
from routes.user_routes import user_bp
from routes.pago_routes import pago_bp
from routes.resena_routes import resena_bp
from routes.direccion_routes import direccion_bp

# Registrar las rutas
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(category_bp, url_prefix='/api/categories')
app.register_blueprint(product_category_bp, url_prefix='/api/products_categories')
app.register_blueprint(pedido_bp, url_prefix='/api/pedidos')
app.register_blueprint(detalle_bp, url_prefix='/api/detalles_pedidos')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(pago_bp, url_prefix='/api/pagos')
app.register_blueprint(resena_bp, url_prefix='/api/resenas')
app.register_blueprint(direccion_bp, url_prefix='/api/direcciones')


@app.route('/')
def home():
    return 'Hello, World !'

if __name__ == '__main__':
    app.run(debug=True)
