import os
from alumnium import Alumni
from selenium.webdriver import Chrome
from pytest import fixture

from src.config_util import get_test_config


@fixture(autouse=True)
def init_test():
    test_config = get_test_config()
    os.environ["OPENAI_API_KEY"] = test_config['OPENAI_API_KEY']

def test_search():
    driver = Chrome()
    driver.get("https://duckduckgo.com")
    al = Alumni(driver)
    al.do("search for selenium")
    al.check("page title contains selenium")
    al.check("search results contain selenium.dev")
    assert al.get("atomic number") == 34