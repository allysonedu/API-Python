from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = "minha-chave-secret15487"
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///ecommerce.db' # configuração do banco

login_manager = LoginManager()
 
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login' # autentication of login
CORS(app)


# table of user
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)

# table of product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()

    if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully"}), 200
    return jsonify({"message": "Invalid username or password"}), 401;   


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200;
# router of created Products
@app.route('/api/products/add', methods=["POST"]) # POST create product
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
      product = Product(name=data["name"], price=data["price"], description=data.get("description", "")) # created product and saved in base of database.
      db.session.add(product)
      db.session.commit()  # commit changes to database
      return jsonify({"message": "Product added successfully"})
    return jsonify({"message": "Invalid product data"}), 400 # return product created
    
    

# router of deleted product
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"]) # DELETE delete product
@login_required

def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()  # commit changes to database
        return jsonify({"message": "Product deleted successfully"})
    return jsonify({"message": "Product not found"}), 404 # return product deleted

    
# get product
@app.route('/api/products/<int:product_id>', methods=["GET"]) 
@login_required

def get_product(product_id):
    product = Product.query.get(product_id)
    if product: 
        return jsonify({
            "id": product.id, 
            "name": product.name, 
            "price": product.price, 
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404 # return product not found

#put product Update 
@app.route('/api/products/update/<int:product_id>', methods=["PUT"]) 
@login_required

def update_product(product_id):
    product = Product.query.get(product_id)
    if not product: 
        return jsonify({"message": "Product not found"}), 404 # return product not found
    
    data = request.json
    if 'name' in data: 
        product.name = data["name"]

    if 'price' in data:
        product.price = data["price"]        
    
    if 'description' in data:
        product.description = data["description"]

    db.session.commit()  # commit changes to database  

    return jsonify({"message": "Product updated successfully"})    



@app.route('/api/products', methods=['GET'])
@login_required

def get_products():
    products = Product.query.all()
    products_list = []
    for product in products:
        product_data = {
            "id": product.id, 
            "name": product.name, 
            "price": product.price, 
            "description": product.description
        }
        products_list.append(product_data)
    return jsonify(products_list)


#Checkout

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    #Usuario
    user = User.query.get(int(current_user.id))
    # Produto
    product = Product.query.get(product_id)

    if user and product: 
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()  
        return jsonify({'message': 'Item added successfully'})
    return jsonify({'message': 'Failed to add item to cart found'}), 400
      

if __name__ == '__main__':
    app.run(debug=True)


