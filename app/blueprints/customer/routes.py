from marshmallow import ValidationError
from flask import request, jsonify
from sqlalchemy import select
from .schemas import customer_schema, customers_schema
from app.models import db, Customer
from . import customers_bp


@customers_bp.route('/', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({'error': 'Email already associated with a customer'})
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#GET ALL CUSTOMERS
@customers_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)

#GET SPECIFIC CUSTOMER
@customers_bp.route("//<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

#UPDATE SPECIFIC CUSTOMER
@customers_bp.route("//<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#DELETE SPECIFIC CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = db.session.get(Customer, customer_id)

        if not customer:
            return jsonify({"error": "Customer not found."}), 404

        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200
    
    except Exception as e:
        print(f'error deleting cutomer: {e}')
        return jsonify({"error": 'internal server error'}), 500