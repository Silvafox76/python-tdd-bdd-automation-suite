import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "sqlite:///:memory:"
)

class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def test_create_a_product(self):
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)

    def test_add_a_product(self):
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

    def test_read_a_product(self):
        product = ProductFactory()
        product.create()
        found = Product.find(product.id)
        self.assertIsNotNone(found)

    def test_update_a_product(self):
        product = ProductFactory()
        product.create()
        product.name = "Updated Name"
        product.price = Decimal("99.99")
        product.update()
        updated = Product.find(product.id)
        self.assertEqual(updated.name, "Updated Name")

    def test_update_without_id_raises(self):
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        product = ProductFactory()
        product.id = 1
        data = product.serialize()
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["price"], str(product.price))
        self.assertIn("available", data)
        self.assertIn("category", data)

    def test_deserialize_a_product(self):
        data = {
            "name": "Book",
            "description": "Paperback",
            "price": "15.50",
            "available": True,
            "category": "HOUSEWARES"
        }
        product = Product().deserialize(data)
        self.assertEqual(product.name, "Book")
        self.assertEqual(product.price, Decimal("15.50"))
        self.assertEqual(product.category, Category.HOUSEWARES)

    def test_deserialize_bad_available_type(self):
        data = {
            "name": "Test",
            "description": "Bad Bool",
            "price": "10.00",
            "available": "yes",
            "category": "FOOD"
        }
        with self.assertRaises(DataValidationError):
            Product().deserialize(data)

    def test_deserialize_missing_fields(self):
        with self.assertRaises(DataValidationError):
            Product().deserialize({})

    def test_find_by_name(self):
        product = ProductFactory(name="UniqueName")
        product.create()
        results = Product.find_by_name("UniqueName")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].name, "UniqueName")

    def test_find_by_price(self):
        product = ProductFactory(price=Decimal("19.99"))
        product.create()
        results = Product.find_by_price("19.99")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].price, Decimal("19.99"))

    def test_find_by_availability(self):
        ProductFactory(available=True).create()
        ProductFactory(available=False).create()
        available_products = Product.find_by_availability(True)
        unavailable_products = Product.find_by_availability(False)
        self.assertTrue(all(p.available for p in available_products))
        self.assertTrue(all(not p.available for p in unavailable_products))

    def test_find_by_category(self):
        product = ProductFactory(category=Category.TOOLS)
        product.create()
        results = Product.find_by_category(Category.TOOLS)
        self.assertEqual(results[0].category, Category.TOOLS)
