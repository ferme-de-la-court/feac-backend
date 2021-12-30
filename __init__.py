# -*- coding: utf-8 -*-

import os
import os.path
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
import toml
from farmer.rest import cors, check_token, generate_token
from farmer.utils import FarmerEncoder

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_file("etc/farmer.toml", load=toml.load)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.json_encoder = FarmerEncoder

    db.init_app(app)
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(inject_sample_cmd)

    from farmer import catalog

    catalog.shopping.after_request(cors)
    app.register_blueprint(catalog.shopping)

    catalog.auth.after_request(cors)
    app.register_blueprint(catalog.auth)

    catalog.shed.after_request(cors)
    catalog.shed.after_request(generate_token)
    catalog.shed.before_request(check_token)
    app.register_blueprint(catalog.shed)

    return app

def init_db():
    db.drop_all()
    db.create_all()


@click.command("inject-sample")
@with_appcontext
def inject_sample_cmd():
    init_db()

    from farmer.catalog import Product, Price, Category, Delivery

    pdt = Category(name="pomme de terre")
    veg = Category(name="légumes")
    db.session.add(pdt)
    db.session.add(veg)

    bintje = Product(name="bintje", desc="pomme de terre delicieuse pour les frites")
    bintje.prices.append(Price(amount=4.5, unit="kg"))
    bintje.prices.append(Price(amount=20, quantity=5, unit="kg"))
    bintje.categories.append(pdt)
    bintje.categories.append(veg)
    db.session.add(bintje)

    charl = Product(name="charlotte", desc="pomme de terre idéale pour les purées et la cuison vapeure")
    charl.prices.append(Price(amount=6, unit="kg"))
    charl.prices.append(Price(amount=25, quantity=5, unit="kg"))
    charl.categories.append(pdt)
    charl.categories.append(veg)
    db.session.add(charl)

    cdt = Delivery(distance=20, amount=60)
    db.session.add(cdt)
    cdt = Delivery(distance=30, amount=80)
    db.session.add(cdt)
    cdt = Delivery(distance=40, amount=90)
    db.session.add(cdt)
    cdt = Delivery(distance=60, amount=100)
    db.session.add(cdt)

    db.session.commit()

    click.echo("sample data injected")

@click.command("init-db")
@with_appcontext
def init_db_cmd():
    init_db()
    click.echo("database initialized")
