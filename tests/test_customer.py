from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name='test_user', email='test@email.com', address='1 test street', phone='123-456-7890', password='password123')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def get_auth_token(self):
        credentials = {
            'email': 'test@email.com',
            'password': 'password123'
        }
        response = self.client.post('/customers/login', json=credentials)
        return response.json['auth_token']


    def test_create_customer(self):
        customer_payload = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone': '123-456-7890',
            'address': '123 street',
            'password': 'password123'
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')

    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            # Missing email field for testing
            "phone": "123-456-7890",
            "address": "123 street",     
            "password": "password123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])

    def test_login_customer(self):
        credentials = {
            'email': 'test@email.com',
            'password': 'password123'
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('auth_token', response.json)
    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_password"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')

    def test_update_customer(self):
        update_payload = {
            "name": "Paul",
            "email":"test@email.com"
        }

        headers = {'Authorization': "Bearer " + self.get_auth_token()}

        response = self.client.put('/customers/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Paul') 
        self.assertEqual(response.json['email'], 'test@email.com')    