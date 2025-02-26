from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Create a new Chrome WebDriver instance
driver = webdriver.Chrome(options=options)

# Navigate to a website
driver.get("https://syntystore.com/products/polygon-battle-royale-pack?_pos=1&_sid=fba0783cf&_ss=r")

# Get the html page source of the current page
page_source = driver.page_source

# Close the browser window
driver.quit()

soup = BeautifulSoup(page_source, features="lxml")

results = soup.find(id="tiny-tabs-content-1")

titles = results.find_all('strong')
print(titles)
messages = results.find_all('span')

inventory = ""

for msg in titles:
    temp = msg.text.strip()
    temp = temp.strip(',') + ","
    if (temp != ","):
        inventory += temp

inventory = inventory.replace(",", "\n")

file_to_write = open("page_source.txt", "w", encoding="utf-8")
file_to_write.write(inventory)
file_to_write.close()

vehicles = []
characters = []
ranged_weapons = []
melee_weapons = []
