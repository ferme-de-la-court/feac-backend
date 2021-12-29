from flask import Blueprint, request
from .models import Product, Delivery, Order
from farmer.rest import handle
from farmer.notif import notify

shopping = Blueprint("catalog", __name__, url_prefix="/catalog")

@shopping.route("/products", methods=["GET"])
@handle(code=200)
def catalog():
    """get the list of available products"""
    return Product.query.all()


@shopping.route("/deliveries", methods=["GET"])
@handle(code=200)
def deliveries():
    """get the list of available delivery prices"""
    return Delivery.query.all()


@shopping.route("/orders/", methods=["POST"])
@handle(code=201)
def create_order():
    """create a new order"""
    p = Order.create(request.json)
    try:
        notify()
    except Exception:
        pass
    return p
