######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product Steps

Steps file for products.feature
"""

import requests
from behave import given
from service.common import status

# HTTP Status Codes
HTTP_200_OK = status.HTTP_200_OK
HTTP_201_CREATED = status.HTTP_201_CREATED
HTTP_204_NO_CONTENT = status.HTTP_204_NO_CONTENT

@given('the following products')
def step_impl(context):
    """ Delete all Products and load new ones """
    rest_endpoint = f"{context.base_url}/products"

    # Step 1: List all existing products
    context.resp = requests.get(rest_endpoint)
    print(f"GET {rest_endpoint} => {context.resp.status_code}")
    assert context.resp.status_code in [HTTP_200_OK, HTTP_201_CREATED]

    # Step 2: Delete all existing products
    for product in context.resp.json():
        delete_url = f"{rest_endpoint}/{product['id']}"
        resp = requests.delete(delete_url)
        print(f"DELETE {delete_url} => {resp.status_code}")
        assert resp.status_code == HTTP_204_NO_CONTENT

    # Step 3: Create new products from the scenario table
    for row in context.table:
        data = {
            "name": row["name"],
            "description": row["description"],
            "price": float(row["price"]),
            "available": row["available"].lower() == "true",
            "category": row["category"]
        }
        context.resp = requests.post(rest_endpoint, json=data)
        print(f"POST {rest_endpoint} => {context.resp.status_code}")
        assert context.resp.status_code == HTTP_201_CREATED
