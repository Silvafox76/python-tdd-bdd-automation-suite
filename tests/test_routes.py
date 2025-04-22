######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
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

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
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

    ######################################################################
    # Utility Methods
    ######################################################################
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

    ######################################################################
    # Test Index + Health
    ######################################################################
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    ######################################################################
    # CREATE Tests
    ######################################################################
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

    ######################################################################
    # READ A PRODUCT - Happy Path
    ######################################################################
    def test_get_product(self):
        """It should Get a single Product"""
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    ######################################################################
    # READ A PRODUCT - Sad Path
    ######################################################################
    def test_get_product_not_found(self):
        """It should not Get a Product that's not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    ######################################################################
    # UPDATE A PRODUCT
    ######################################################################
    def test_update_product(self):
        """It should Update an existing Product"""
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_product = response.get_json()
        new_product["description"] = "unknown"

        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "unknown")

    ######################################################################
    # DELETE A PRODUCT
    ######################################################################
    def test_delete_product(self):
        """It should Delete a Product"""
        products = self._create_products(3)
        product_count = self.get_product_count()
        test_product = products[0]

        # Delete the product
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # Ensure it's gone
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify the count is reduced
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    ######################################################################
    # Test List By Name
    ######################################################################
    def test_list_products_by_name(self):
        """It should list products by name"""
        product = ProductFactory(name="UniqueName")
        product.create()

        response = self.client.get("/products", query_string={"name": "UniqueName"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["name"], "UniqueName")
    
    ######################################################################
    # Test List By Category
    ######################################################################
    
    def test_list_products_by_category(self):
        """It should list products by category"""
        product = ProductFactory(category=Category.FOOD)
        product.create()

        response = self.client.get("/products", query_string={"category": "FOOD"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["category"], "FOOD")

    ######################################################################
    # Test List By Availability
    ######################################################################

    def test_list_products_by_availability(self):
        """It should list products by availability"""
        product = ProductFactory(available=True)
        product.create()

        response = self.client.get("/products", query_string={"available": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]["available"], True)
    
    ######################################################################
    # Test Invalid Category
    ######################################################################

    def test_list_products_by_invalid_category(self):
        """It should return 400 for invalid category"""
        response = self.client.get("/products", query_string={"category": "INVALID"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       

