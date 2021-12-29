from flask import Blueprint, request
from .models import Product, Delivery, Order
from farmer.rest import handle, make_token

shed = Blueprint("shed", __name__, url_prefix="/shed")


@shed.route("/products/", methods=["POST"])
@handle(code=201)
def create_product():
    """register a new product"""
    return Product.create(request.json)


@shed.route("/products/<int:id>", methods=["PUT"])
@handle(code=200)
def edit_product(id):
    """edit an existing product"""
    return Product.edit(id, request.json)


@shed.route("/products/<int:id>/upload", methods=["POST"])
@handle(code=201)
def upload_image(id):
    return Product.upload(id, request.get_data(cache=False))


@shed.route("/deliveries/", methods=["POST"])
@handle(code=201)
def create_delivery():
    """create a new delivery price"""
    return Delivery.create(request.json)


@shed.route("/deliveries/<int:id>", methods=["PUT"])
@handle(code=200)
def edit_delivery(id):
    """delete an existing delivery price"""
    return Delivery.edit(id, request.json)

@shed.route("/deliveries/<int:id>", methods=["DELETE"])
@handle(code=204)
def delete_delivery(id):
    """delete an existing delivery price"""
    Delivery.delete(id)
    return None


@shed.route("/orders", methods=["GET"])
@handle(code=200)
def orders():
    """get the list of submitted orders"""
    return Order.query.all()
