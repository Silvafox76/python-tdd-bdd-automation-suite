from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@when('I visit the "{page}"')
def step_impl(context, page):
    if page == "Home Page":
        context.driver.get(context.base_url)

@when('I set the "{field}" to "{value}"')
def step_impl(context, field, value):
    field_id = f'product_{field.lower()}'
    element = context.driver.find_element(By.ID, field_id)
    element.clear()
    element.send_keys(value)

@when('I select "{value}" in the "{field}" dropdown')
def step_impl(context, value, field):
    field_id = f'product_{field.lower()}'
    dropdown = context.driver.find_element(By.ID, field_id)
    for option in dropdown.find_elements(By.TAG_NAME, 'option'):
        if option.text == value:
            option.click()
            break

@when('I press the "{button}" button')
def step_impl(context, button):
    button_map = {
        "Create": "create-btn",
        "Update": "update-btn",
        "Delete": "delete-btn",
        "Retrieve": "retrieve-btn",
        "Clear": "clear-btn",
        "Search": "search-btn",
    }
    button_id = button_map.get(button)
    assert button_id is not None, f"Button '{button}' is not defined in button_map"
    context.driver.find_element(By.ID, button_id).click()

@when('I copy the "{field}" field')
def step_impl(context, field):
    field_id = f'product_{field.lower()}'
    context.clipboard = context.driver.find_element(By.ID, field_id).get_attribute('value')

@when('I paste the "{field}" field')
def step_impl(context, field):
    field_id = f'product_{field.lower()}'
    element = context.driver.find_element(By.ID, field_id)
    element.clear()
    element.send_keys(context.clipboard)

@when('I change "{field}" to "{value}"')
def step_impl(context, field, value):
    field_id = f'product_{field.lower()}'
    element = context.driver.find_element(By.ID, field_id)
    element.clear()
    element.send_keys(value)

@then('I should see the message "{message}"')
def step_impl(context, message):
    status_element = context.driver.find_element(By.ID, 'flash_message')
    assert message in status_element.text

@then('the "{field}" field should be empty')
def step_impl(context, field):
    field_id = f'product_{field.lower()}'
    element = context.driver.find_element(By.ID, field_id)
    assert element.get_attribute('value') == ''

@then('the "{field}" field should contain "{value}"')
@then('I should see "{value}" in the "{field}" field')
def step_impl(context, value, field):
    field_id = f'product_{field.lower()}'
    element = context.driver.find_element(By.ID, field_id)
    assert element.get_attribute('value') == value

@then('I should see "{value}" in the "{field}" dropdown')
def step_impl(context, value, field):
    field_id = f'product_{field.lower()}'
    dropdown = context.driver.find_element(By.ID, field_id)
    selected = dropdown.find_element(By.CSS_SELECTOR, 'option:checked')
    assert selected.text == value

@then('I should see "{text}" in the results')
def step_impl(context, text):
    table = context.driver.find_element(By.ID, "search_results")
    assert text in table.text

@then('I should not see "{text}" in the results')
def step_impl(context, text):
    table = context.driver.find_element(By.ID, "search_results")
    assert text not in table.text

@then('I should see "Product Catalog Administration" in the title')
def step_impl(context):
    assert "Product Catalog Administration" in context.driver.title

@then('I should not see "404 Not Found"')
def step_impl(context):
    assert "404 Not Found" not in context.driver.page_source
