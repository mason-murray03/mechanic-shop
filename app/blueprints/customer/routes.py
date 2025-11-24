from marshmallow import ValidationError
from flask import request, jsonify
from sqlalchemy import select
from .schemas import customer_schema, customers_schema, login_schema
from app.models import db, Customer, ServiceTicket
from . import customers_bp
from app.extensions import limiter, cache
from ...utils.util import encode_token, token_required
from ..service_ticket.schemas import service_tickets_schema
from functools import wraps

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify('e.messages'), 400

    email = data['email']
    password = data['password']

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalar_one_or_none()

    if customer and customer.password == password:
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': 'Invalid email or password'}), 401


@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per hour")
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    password = request.json.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({'error': 'Email already associated with a customer'})

    customer_data['password'] = password
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#GET ALL CUSTOMERS
@customers_bp.route("/", methods=['GET'])
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)

        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers)

#GET SPECIFIC CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=['GET'])
@cache.cached(timeout=60)
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

#UPDATE SPECIFIC CUSTOMER
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id, token_customer_id):

    if int(customer_id) != int(token_customer_id):
        print('Token ID  mismatch')
        return jsonify({'message': 'Unauthorized'}), 403

    customer = db.session.get(Customer, customer_id)
    if not customer:
        print('Customer not found')
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json, partial=True)
        print('Parsed customer data')
    except ValidationError as e:
        print('Validation error:', e.messages)
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    print('Customer updated successfully')
    return customer_schema.jsonify(customer), 200

#DELETE SPECIFIC CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
@token_required
def delete_customer(customer_id, token_customer_id):
    print(f"🧨 DELETE route hit: customer_id={customer_id}, token_customer_id={token_customer_id}")

    if int(customer_id) != int(token_customer_id):
        print("🚫 Unauthorized delete attempt")
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            print("❌ Customer not found")
            return jsonify({"error": "Customer not found."}), 404

        db.session.delete(customer)
        db.session.commit()
        print("✅ Customer deleted")
        return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200

    except Exception as e:
        print(f'❌ Error deleting customer: {e}')
        return jsonify({"error": "Internal server error"}), 500


# GET TICKETS FOR SPECIFIC CUSTOMER
@customers_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(tickets), 200
