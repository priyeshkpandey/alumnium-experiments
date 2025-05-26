from datetime import datetime
import os

from playwright.sync_api import Page, sync_playwright
from pytest import fixture, hookimpl
from selenium.webdriver import Chrome
from alumnium import Alumni

from src.config_util import get_test_config

@fixture(scope="session", autouse=True)
def api_key():
    print("Executing init_test...")
    test_config = get_test_config()
    return test_config['OPENAI_API_KEY']


@fixture(scope="session", autouse=True)
def driver(api_key):
    os.environ["OPENAI_API_KEY"] = api_key
    driver = os.getenv("ALUMNIUM_DRIVER", "selenium")
    if driver == "playwright":
        with sync_playwright() as playwright:
            headless = os.getenv("ALUMNIUM_PLAYWRIGHT_HEADLESS", "true") == "true"
            yield playwright.chromium.launch(headless=headless).new_page()
    elif driver == "selenium":
        driver = Chrome()
        yield driver
        driver.quit()
    else:
        raise NotImplementedError(f"Driver {driver} not implemented")


@fixture(scope="session", autouse=True)
def al(driver):
    al = Alumni(driver)
    yield al
    al.quit()


@fixture
def navigate(driver):
    def __navigate(url):
        if isinstance(driver, Chrome):
            driver.get(url)
        elif isinstance(driver, Page):
            driver.goto(url)

    return __navigate


@fixture
def execute_script(driver):
    def __execute_script(script):
        if isinstance(driver, Chrome):
            driver.execute_script(script)
        elif isinstance(driver, Page):
            driver.evaluate(script)

    return __execute_script


@hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    timestamp = datetime.now().strftime("%H-%M-%S")
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        # Add screenshot and URL to the report
        driver = item.funcargs["driver"]
        if isinstance(driver, Chrome):
            driver.save_screenshot(f"/tmp/reports/screenshot-{timestamp}.png")
            url = driver.current_url
        elif isinstance(driver, Page):
            driver.screenshot(path=f"/tmp/reports/screenshot-{timestamp}.png")
            url = driver.url
        extras.append(pytest_html.extras.image(f"screenshot-{timestamp}.png"))
        extras.append(pytest_html.extras.url(url))
        report.extras = extras
        # Process Alumnium cache
        al = item.funcargs["al"]
        if report.passed:
            al.cache.save()
        else:
            al.cache.discard()