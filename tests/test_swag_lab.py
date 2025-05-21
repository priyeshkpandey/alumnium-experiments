from pytest import fixture
from alumnium import Model

@fixture(autouse=True)
def login(al, execute_script, navigate):
    al.learn("add laptop to cart", ["click button 'Add to cart' next to 'laptop' product"])
    al.learn("go to shopping cart", ["click link to the right of 'Swag Labs' header"])
    al.learn("sort products by lowest shipping cost", ["select 'Shipping (low to high)' in sorting dropdown"])

    navigate("https://www.saucedemo.com/")
    al.do("type 'standard_user' into username field")
    al.do("type 'secret_sauce' into password field")
    al.do("click login button")
    yield
    execute_script("window.localStorage.clear()")

    al.planner_agent.prompt_with_examples.examples.clear()


def test_add_to_cart_checkout(al):
    al.do("add onesie to cart")
    al.do("add backpack to cart")
    al.do("go to shopping cart")
    assert al.get("titles of products in cart") == ["Sauce Labs Onesie", "Sauce Labs Backpack"]

    al.do("go to checkout")
    al.do("continue with first name - Al, last name - Um, ZIP - 95122")

    assert al.get("item total without tax") == 37.98
    assert al.get("tax amount") == 3.04
    assert al.get("total amount with tax") == round(37.98 + 3.04, 2)
    assert al.get("shipping details") == "Free Pony Express Delivery!"

    al.do("finish checkout")

    al.check("thank you for the order message is shown")
    if Model.load() not in [Model.AWS_META, Model.DEEPSEEK]:
        al.check("big green checkmark is shown", vision=True)