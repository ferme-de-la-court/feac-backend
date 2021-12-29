from dataclasses import dataclass
from typing import List
import datetime
from sqlalchemy.sql import functions
from farmer import db
from farmer.errors import BadDataException, NotFoundException

categories = db.Table(
    "category_products",
    db.Column('category_id', db.Integer, db.ForeignKey("categories.id"), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey("products.id"), primary_key=True),
)


@dataclass
class Category(db.Model):
    name: str

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    @classmethod
    def get_or_create(cls, name):
        cat = cls.query.filter_by(name=name).first()
        if cat is None:
            cat = cls(name=name)
        return cat


@dataclass
class Price(db.Model):
    id: int
    amount: float
    quantity: int
    unit: str

    __tablename__ = "prices"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit = db.Column(db.String(64), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


@dataclass
class Product(db.Model):
    id: int
    name: str
    desc: str
    image: str
    available: bool
    highlight: bool
    prices: List[Price]
    categories: List[Category]

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    desc = db.Column(db.String(512), nullable=False)
    highlight = db.Column(db.Boolean, nullable=False, default=True)
    available = db.Column(db.Boolean, nullable=False, default=True)
    image = db.Column(db.String, nullable=True)
    prices = db.relationship('Price', backref='product', lazy=True)
    categories = db.relationship('Category', secondary=categories, lazy='subquery')

    @classmethod
    def create(cls, data):
        p = cls(name=data.get("name"), desc=data.get("desc"))
        p.highlight = data.get("highlight", False)
        p.available = data.get("available", True)
        p.categories = [Category.get_or_create(c) for c in data.get("categories", [])]

        for i in data.get("prices", []):
            if not isinstance(i, dict):
                raise BadDataException("expected object for price")

            r = Price(
                amount=i.get("amount"),
                quantity=i.get("quantity", 1),
                unit=i.get("unit", "kg"),
            )
            p.prices.append(r)

        db.session.add(p)
        db.session.commit()
        return p

    @classmethod
    def edit(cls, id, data):
        p = cls.query.filter_by(id=id).first()
        if p is None:
            raise NotFoundException("product not found")

        p.name = data.get("name", p.name)
        p.desc = data.get("desc", p.desc)
        p.available = data.get("available", p.available)
        p.highlight = data.get("highlight", p.highlight)
        p.categories[:] = []
        p.categories = [Category.get_or_create(c) for c in data.get("categories", [])]

        for i in p.prices:
            db.session.delete(i)
        
        for i in data.get("prices", []):
            if not isinstance(i, dict):
                raise BadDataException("expected object for price")

            r = Price(
                amount=i.get("amount"),
                quantity=i.get("quantity", 1),
                unit=i.get("unit", "kg"),
            )
            p.prices.append(r)

        db.session.add(p)
        db.session.commit()
        return p

    @classmethod
    def upload(cls, id, data):
        p = cls.query.filter_by(id=id).first()
        if p is None:
            raise NotFoundException("product not found")

        p.image = data.hex()
        db.session.add(p)
        db.session.commit()
        return None



@dataclass
class Delivery(db.Model):
    id: int
    distance: int
    amount: int

    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Integer, nullable=False, default=0)
    amount = db.Column(db.Integer, nullable=False, default=0)

    @classmethod
    def create(cls, data):
        d = cls(**data)
        db.session.add(d)
        db.session.commit()
        return d


    @classmethod
    def edit(cls, id, data):
        d = cls.query.filter_by(id=id).first()
        if d is None:
            raise NotFoundException("delivery not found")

        d.distance = data.get("distance", d.distance)
        d.amount = data.get("amount", d.amount)
        db.session.add(d)
        db.session.commit()
        return d


    @classmethod
    def delete(cls, id):
        d = cls.query.filter_by(id=id).first()
        if d is None:
            return
        db.session.delete(d)
        db.session.commit()

@dataclass
class Contact(db.Model):
    id: int
    name: str
    phone: str
    email: str

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(16), nullable=True)
    email = db.Column(db.String(128), nullable=True)

    @classmethod
    def create(cls, data):
        return cls(**data)

class Address(db.Model):
    id: int
    street: str
    city: str
    country: str

    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(128))
    city = db.Column(db.String(64), nullable=True)
    country = db.Column(db.String(64), nullable=True)

    @classmethod
    def create(cls, data):
        return cls(**data)

@dataclass
class Order(db.Model):
    id: int

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, server_default=functions.now())
    when = db.Column(db.Date, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    contact = db.relationship('Contact', lazy=True)
    addr_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=True)
    address = db.relationship("Address", lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True)

    @classmethod
    def create(cls, data):
        o = cls(when=datetime.date.fromisoformat(data.get("when")))
        contact = data.get("contact", None)
        if contact is None:
            raise BadDataException("missing contact information")
        o.contact = Contact.create(contact)
        address = data.get("address", None)
        if address is not None:
            o.address = Address.create(address)

        products = data.get("products", [])
        if not isinstance(products, list):
            raise BadDataException("expected products being a list")
        for p in products:
            item = OrderItem(
                product_id=p.get("product"),
                quantity=p.get("quantity", 1),
                amount=p.get('amount'),
                unit=p.get('unit'),
            )
            o.items.append(item)

        db.session.add(o)
        db.session.commit()
        return o

@dataclass
class OrderItem(db.Model):
    amount: float
    quantity: int
    unit: str

    __tablename__ = "order_items"

    product_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit = db.Column(db.String(64), nullable=False)
