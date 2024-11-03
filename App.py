from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///ecommerce.db' # configuração do banco
 
db = SQLAlchemy(app)

# table of product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

# router of created Products
@app.route('/api/products/add', methods=["POST"]) # POST create product
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
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()  # commit changes to database
        return jsonify({"message": "Product deleted successfully"})
    return jsonify({"message": "Product not found"}), 404 # return product deleted

    
@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)


