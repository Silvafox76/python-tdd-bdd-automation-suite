"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver
from behave import fixture, use_fixture
import requests
from service import app
from service.models import db

# Constants
WAIT_SECONDS = int(getenv('WAIT_SECONDS', '30'))
BASE_URL = getenv('BASE_URL', 'http://localhost:8080')
DRIVER = getenv('DRIVER', 'firefox').lower()
DATABASE_URI = getenv('DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/postgres')

######################################################################
# Before and After Hooks for Selenium
######################################################################
def before_all(context):
    """Executed once before all tests"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS
    # Set up WebDriver
    if 'firefox' in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.config.setup_logging()

def after_all(context):
    """Executed once after all tests"""
    context.driver.quit()

######################################################################
# Behave Fixture to reset DB using Flask app context
######################################################################
@fixture
def setup_db(context, *args, **kwargs):
    """Resets the DB schema before each scenario (optional)"""
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.app_context():
        db.drop_all()
        db.create_all()
        context.client = app.test_client()
    yield context.client

def before_scenario(context, scenario):
    """Executed before each scenario"""
    use_fixture(setup_db, context)
    context.products = []

######################################################################
# Utility functions to create web drivers
######################################################################
def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
