from . import db

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(18), nullable=False)
    address = db.Column(db.String(50), nullable=False)  
    ban = db.Column(db.Boolean, default=False)
    admin_status = db.Column(db.Boolean, default=False)

    account_purchases = db.relationship("AccountPurchase", back_populates="account")
    orders = db.relationship("Order", back_populates="account")

    def profile_to_dict(self):
        return {"id": self.id, "email": self.email, "password": self.password, "name": self.name, "address": self.address}

class AccountPurchase(db.Model):
    __tablename__ = "account_purchases"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(18), nullable=False)
    
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    
    account = db.relationship("Account", back_populates="account_purchases")
    product = db.relationship("Product", back_populates="account_purchases")

    def to_dict(self):
        return {"id": self.id,  "product_name": self.product_name, "account_id": self.account_id, "product_id": self.product_id}

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(18), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    
    category = db.relationship("Category", back_populates="products")
    account_purchases = db.relationship("AccountPurchase", back_populates="product")
    orders = db.relationship("Order", back_populates="product")

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(18), nullable=False, unique=True)
    
    products = db.relationship("Product", back_populates="category")

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(18), default="new")
    
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    
    account = db.relationship("Account", back_populates="orders")
    product = db.relationship("Product", back_populates="orders")

    def to_dict(self):
        return {"id": self.id, "status": self.status, "account_id": self.account_id, "product_id": self.product_id}




    

