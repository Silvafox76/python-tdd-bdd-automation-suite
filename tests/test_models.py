import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///:memory:")


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
        """It should Create a product and assert that it exists"""
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
        """It should add a Product to the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.create()
        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_update_without_id_raises(self):
        """It should raise error if update is called without ID"""
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        product.id = 1
        data = product.serialize()
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["price"], str(product.price))
        self.assertIn("available", data)
        self.assertIn("category", data)

    def test_deserialize_a_product(self):
        """It should deserialize a Product"""
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
        """It should raise error for bad available type"""
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
        """It should raise error for missing fields"""
        with self.assertRaises(DataValidationError):
            Product().deserialize({})

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(5):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        expected = len([p for p in products if p.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(len(found), expected)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        expected = len([p for p in products if p.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(len(found), expected)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        expected = len([p for p in products if p.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(len(found), expected)
        for product in found:
            self.assertEqual(product.category, category)
