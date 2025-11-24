import unittest
from app import create_app
from app.models import Inventory, db

class TestInventoryRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
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

    def test_add_inventory(self):
        resp = self.client.post("/inventory/", json={"name": "Brake Pads", "price": 49.99})
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["name"], "Brake Pads")

    def test_get_inventory(self):
        with self.app.app_context():
            db.session.add(Inventory(name="Oil Filter", price=9.99))
            db.session.commit()

        resp = self.client.get("/inventory/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(item["name"] == "Oil Filter" for item in data))

    def test_get_part(self):
        with self.app.app_context():
            part = Inventory(name="Spark Plug", price=3.50)
            db.session.add(part)
            db.session.commit()
            part_id = part.id

        resp = self.client.get(f"/inventory/{part_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "Spark Plug")

    def test_update_part(self):
        with self.app.app_context():
            part = Inventory(name="Air Filter", price=15.00)
            db.session.add(part)
            db.session.commit()
            part_id = part.id

        resp = self.client.put(f"/inventory/{part_id}", json={"price": 19.99})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["price"], 19.99)

    def test_delete_part(self):
        with self.app.app_context():
            part = Inventory(name="Battery", price=120.00)
            db.session.add(part)
            db.session.commit()
            part_id = part.id

        resp = self.client.delete(f"/inventory/{part_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("successfully deleted", data["message"])

if __name__ == "__main__":
    unittest.main()



