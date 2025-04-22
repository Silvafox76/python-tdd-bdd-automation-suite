######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# https://www.apache.org/licenses/LICENSE-2.0
######################################################################

"""
Product API Service Test Suite
"""

import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product, Category
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_products(self, count: int = 1) -> list:
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def get_product_count(self):
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    def test_create_product(self):
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

    def test_create_product_with_no_name(self):
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_product(self):
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product(self):
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_product = response.get_json()
        new_product["description"] = "updated"

        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "updated")

    def test_delete_product(self):
        products = self._create_products(3)
        product_count = self.get_product_count()
        test_product = products[0]

        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_list_products_by_name(self):
        product = ProductFactory(name="UniqueName")
        product.create()

        response = self.client.get("/products", query_string={"name": "UniqueName"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["name"], "UniqueName")

    def test_list_products_by_category(self):
        product = ProductFactory(category=Category.FOOD)
        product.create()

        response = self.client.get("/products", query_string={"category": "FOOD"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["category"], "FOOD")

    def test_list_products_by_availability(self):
        product = ProductFactory(available=True)
        product.create()

        response = self.client.get("/products", query_string={"available": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["available"], True)

    def test_list_products_by_invalid_category(self):
        response = self.client.get("/products", query_string={"category": "INVALID"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    # New Error Handler Tests for Full Coverage
    ######################################################################

    def test_error_404_handler(self):
        """It should return 404 for invalid endpoint"""
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Not Found", response.get_data(as_text=True))

    def test_error_405_handler(self):
        """It should return 405 for invalid method"""
        response = self.client.put("/products")
        self.assertEqual(response.status_code, 405)
        self.assertIn("Method not Allowed", response.get_data(as_text=True))

    def test_error_415_handler(self):
        """It should return 415 for bad content type"""
        response = self.client.post("/products", data="text/plain", content_type="text/plain")
        self.assertEqual(response.status_code, 415)
        self.assertIn("Unsupported Media Type", response.get_data(as_text=True))

    def test_error_400_handler(self):
        """It should return 400 for bad request payload"""
        response = self.client.post("/products", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bad Request", response.get_data(as_text=True))
