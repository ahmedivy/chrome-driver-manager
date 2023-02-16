from selenium import webdriver

# Import the driver manager
from drivers_manager import CDM

# Get the path to the driver, it will automatically downloads if required
path = CDM().getPath()

driver = webdriver.Chrome(path)

driver.get("https://www.google.com")