from flask import current_app as app, request, jsonify, Blueprint 
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .models import Account, AccountPurchase, Product, Category, Order 
from . import db
from .utils import encrypt, decrypt


shop_bp = Blueprint("shop", __name__, url_prefix="/shop")
acc_bp =  Blueprint("account",__name__,url_prefix="/account")
admin_bp = Blueprint("admin",__name__,url_prefix="/admin")
product_bp = Blueprint("product",__name__,url_prefix="/product")

shop_bp.register_blueprint(acc_bp)
shop_bp.register_blueprint(admin_bp)
shop_bp.register_blueprint(product_bp)

@acc_bp.route("/register", methods=["POST"])
def reg_acc():
    if request.is_json:
        data = request.get_json()
        if len(data) != 4:
            return jsonify({"ok": False, "message":"by register you need to have email, addres, password and name"}), 401
        keys = ["email", "password", "name", "address"]
        for key in data:
            if key not in keys:
                return jsonify({"ok": False, "message":"by register you need to have email, addres, password and name"}), 400
        exist_account = Account.query.filter_by(email=data["email"]).first()
        if exist_account:
            return jsonify({"ok": False, "message": "Email already exists"}), 400
        account = Account(email = data["email"], password=encrypt(data["password"], 5), name=data["name"], address=data["address"])
        db.session.add(account)
        db.session.commit()
        token = create_access_token(str(account.id))
        refresh_token = create_refresh_token(str(account.id))
        return jsonify({"token": token, "refresh_token":refresh_token})
    return jsonify({"ok": False, "message": "request must be JSON"}), 400

@acc_bp.route("/login", methods=["POST"])
def login_account():
    if request.is_json:
        data = request.get_json()
        if len(data) != 2:
            return jsonify({"ok": False, "message":"by login you need to have email and password"}), 401
        keys = ["email","password"]
        for key in data:
            if key not in keys:
                return jsonify({"ok": False, "message":"by login you need to have email and password"}), 400
        account = Account.query.filter(Account.email==data["email"]).first()
        if account:
            if decrypt(account.password) == data["password"]:
                token = create_access_token(str(account.id))
                refresh_token = create_refresh_token(str(account.id))
                return jsonify({"token": token, "refresh_token":refresh_token})
            return jsonify({"ok": False, "message": "not right password"}), 401
        return jsonify({"ok": False, "message": "accont not exist"}), 404
    return jsonify({"ok": False, "message": "request must be JSON"}), 400

@acc_bp.route("/profile", methods=["GET"])
@jwt_required()
def account_profile():
    acc_id = get_jwt_identity()
    account = Account.query.filter_by(id=acc_id).first()
    if account:
        account_purchases = []
        for purchase in account.account_purchases:  
            account_purchases.append(purchase.to_dict())
        return jsonify({"ok": True, "message": [account.profile_to_dict(), account_purchases]})
    return jsonify({"ok": False, "message": "not right token"}), 400

@product_bp.route("/account/buy/<int:prod_id>", methods=["POST"])
@jwt_required()
def buy_product_acc(prod_id):
    product = Product.query.filter(Product.id == prod_id).first()
    if product:
        acc_id = get_jwt_identity()
        account = Account.query.filter(Account.id == acc_id).first()
        if account:
            if account.ban:
                return jsonify({"ok": False, "message": "Your account is banned"}), 403
            purshes_product = AccountPurchase(product_name=product.name, account=account, account_id=account.id, product=product, product_id=product.id)  
            db.session.add(purshes_product)
            order = Order(status = "new", account_id = account.id, product_id = product.id)
            db.session.add(order)
            db.session.commit()
            return jsonify({"ok":True, "message": "product bought successes"})
        return jsonify({"ok": False, "message":"not right token"}), 400
    return jsonify({"ok": False, "message": "product id out of range"}), 400

@product_bp.route("/guest/buy/<int:prod_id>", methods=["POST"])
def buy_product_guest(prod_id):
    product = Product.query.filter(Product.id == prod_id).first()
    if product:
        data = request.get_json()
        if len(data) != 2:
            return jsonify({"ok": False, "message":"by register you need to have addres and name"}), 401
        keys = ["name", "address"]
        for key in data:
            if key not in keys:
                return jsonify({"ok": False, "message":"by register you need to have addres and name"}), 400
        order = Order(status = "new", account_id = None, product_id = product.id)
        db.session.add(order)
        db.session.commit()
        return jsonify({"ok":True, "message": "product bought successes"})
    return jsonify({"ok": False, "message": "product id out of range"}), 400

@product_bp.route("/", methods=["GET"])
def get_products():
    products_dict = {}  
    categories = Category.query.all()
    for category in categories:
        category_data = {"category_id": category.id,"products": []}
        for product in category.products:  
            category_data["products"].append({"product_id": product.id, "product_name": product.name, "price": product.price})
        products_dict[category.name] = category_data
    return jsonify({"ok": True, "message": products_dict})

@admin_bp.route("/product/add", methods=["POST"])
@jwt_required()
def add_product():
    if request.is_json:
        id = get_jwt_identity()
        account = Account.query.filter(Account.id == id, Account.admin_status==True).first()
        if account:
            data = request.get_json()
            if len(data) != 3:
                return jsonify({"ok": False, "message":"by adding s product you need to have name, price and category_id"}), 401
            keys = ["name","price", "category_id"]
            for key in data:
                if key not in keys:
                    return jsonify({"ok": False, "message":"by adding s product you need to have name, price and category_id"}), 400
            category = Category.query.filter(Category.id == data["category_id"]).first()
            if category:
                exist_product = Product.query.filter_by(name=data["name"]).first()
                if exist_product:
                    return jsonify({"ok": False, "message": "Product with this name already exists"}), 400
                product = Product(name=data["name"], price=data["price"], category_id = data["category_id"])
                db.session.add(product)
                db.session.commit()
                return jsonify({"ok": True, "message": "new product added successe"})
            return jsonify({"ok":False, "message": "category_id out of range"}),400
        return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404
    return jsonify({"ok": False, "message": "request must be JSON"}), 400

@admin_bp.route('/product/delete/<int:prod_id>', methods=["DELETE"])
@jwt_required()
def del_product(prod_id):
    acc_id = get_jwt_identity()
    account = Account.query.filter(Account.id == acc_id, Account.admin_status==True).first()
    if account:
        product = Product.query.filter(Product.id == prod_id).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"ok": True, "message": "product deleted successes"})
        return jsonify({"ok": False, "message": "product id is out of range"}), 400
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404

@admin_bp.route("/product/change/<int:prod_id>", methods=["PUT"])
@jwt_required()
def change_product(prod_id):
    acc_id = get_jwt_identity()
    account = Account.query.filter(Account.id == acc_id, Account.admin_status==True).first()
    if account:
        args = request.args
        product = Product.query.filter(Product.id == prod_id).first()
        if product:
            if "name" in args:
                product.name = args["name"]
            if "price" in args:
                product.price = args["price"]
            if "category_id" in args:
                product.category_id = args["category_id"]
            db.session.commit()
            return jsonify({"ok": True, "message": "product info changed successes"})
        return jsonify({"ok": False, "message": "product id is out of range"}), 400
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404

@admin_bp.route("/category/add", methods=["POST"])
@jwt_required()
def add_category():
    if request.is_json:
        id = get_jwt_identity()
        account = Account.query.filter(Account.id == id, Account.admin_status==True).first()
        if account:
            data = request.get_json()
            if "name" not in data:
                return jsonify({"ok": False, "message":"by adding a category you need to have only name"}), 400
            category = Category.query.filter(Category.name == data["name"]).first()
            if category is None:
                category = Category(name=data["name"])
                db.session.add(category)
                db.session.commit()
                return jsonify({"ok": True, "message": "new category added successes"})
            else:
                return jsonify({"ok":False, "message": "that category is created"}),400
        return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404
    return jsonify({"ok": False, "message": "request must be JSON"}), 400

@admin_bp.route('/category/delete/<int:catg_id>', methods=["DELETE"])
@jwt_required()
def del_category(catg_id):
    acc_id = get_jwt_identity()
    account = Account.query.filter(Account.id == acc_id, Account.admin_status==True).first()
    if account:
        category = Category.query.filter(Category.id == catg_id).first()
        if category:
            db.session.delete(category)
            db.session.commit()
            return jsonify({"ok": True, "message": "category deleted successes"})
        return jsonify({"ok": False, "message": "category id is out of range"}), 400
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404

@admin_bp.route("/category/change/<int:catg_id>", methods=["PUT"])
@jwt_required()
def change_category(catg_id):
    acc_id = get_jwt_identity()
    account = Account.query.filter(Account.id == acc_id, Account.admin_status==True).first()
    if account:
        args = request.args
        category = Category.query.filter(Product.id == catg_id).first()
        if category:
            if "name" in args:
                category.name = args["name"]
            db.session.commit()
            return jsonify({"ok": True, "message": "category info changed successes"})
        return jsonify({"ok": False, "message": "category id is out of range"}), 400
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404

@admin_bp.route("/order/status/<int:ord_id>", methods=["GET"])
@jwt_required()
def order_status(ord_id):
    acc_id = get_jwt_identity()
    account = Account.query.filter(Account.id == acc_id, Account.admin_status==True).first()
    if account:
        order = Order.query.filter(Order.id == ord_id).first()
        if order:
            return jsonify({"ok":True, "message": order.to_dict()})
        return jsonify({"ok":False, "message": "order id is out of range"}), 400
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404

@admin_bp.route("/account/ban/<int:acc_id>", methods=["PUT"])
@jwt_required()
def acc_ban(acc_id):
    adm_id = get_jwt_identity()
    account_adm = Account.query.filter(Account.id == adm_id, Account.admin_status==True).first()
    if account_adm:
        account_client = Account.query.filter(Account.id == acc_id).first()
        if account_client:
            account_client.ban = True
            db.session.commit()
            return jsonify({"ok":False, "message": "account is successe banned"})
        return jsonify({"ok":False, "message": "account with that id not exist "}), 404
    return jsonify({"ok": False, "message": "that account not exist or your not an admin"}),404