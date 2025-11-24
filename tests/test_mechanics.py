import unittest
from app import create_app
from app.models import Mechanic, db

class TestMechanicRoutes(unittest.TestCase):

    def setUp(self):
        # Create app with default config name, then override for testing
        self.app = create_app("TestingConfig")
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_mechanic(self):
        resp = self.client.post("/mechanics/", json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "salary": 50000
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john@example.com")

    def test_get_mechanics(self):
        with self.app.app_context():
            db.session.add(Mechanic(name="Jane Smith", email="jane@example.com", phone="555-5678", salary=60000))
            db.session.commit()

        resp = self.client.get("/mechanics/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(m["name"] == "Jane Smith" for m in data))

    def test_get_mechanic(self):
        with self.app.app_context():
            mech = Mechanic(name="Mike", email="mike@example.com", phone="555-9999", salary=45000)
            db.session.add(mech)
            db.session.commit()
            mech_id = mech.id

        resp = self.client.get(f"/mechanics/{mech_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "Mike")

    def test_update_mechanic(self):
        with self.app.app_context():
            mech = Mechanic(name="Alex", email="alex@example.com", phone="555-0000", salary=40000)
            db.session.add(mech)
            db.session.commit()
            mech_id = mech.id

        resp = self.client.put(f"/mechanics/{mech_id}", json={
            "name": "Alex Updated",
            "email": "alex@example.com",
            "phone": "555-0000",
            "salary": 42000
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "Alex Updated")
        self.assertEqual(data["salary"], 42000)

    def test_delete_mechanic(self):
        with self.app.app_context():
            mech = Mechanic(name="Delete Me", email="delete@example.com", phone="555-1111", salary=38000)
            db.session.add(mech)
            db.session.commit()
            mech_id = mech.id

        resp = self.client.delete(f"/mechanics/{mech_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("successfully deleted", data["message"])

    def test_popular_mechanics(self):
        with self.app.app_context():
            mech1 = Mechanic(name="Pop1", email="pop1@example.com", phone="555-2222", salary=35000)
            mech2 = Mechanic(name="Pop2", email="pop2@example.com", phone="555-3333", salary=36000)
            db.session.add_all([mech1, mech2])
            db.session.commit()

        resp = self.client.get("/mechanics/popular")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)

    def test_most_active_mechanics(self):
        with self.app.app_context():
            mech = Mechanic(name="Active", email="active@example.com", phone="555-4444", salary=37000)
            db.session.add(mech)
            db.session.commit()

        resp = self.client.get("/mechanics/most-active")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)

if __name__ == "__main__":
    unittest.main()
