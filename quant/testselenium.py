from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import date, datetime

start_program_time = datetime.now()
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path='/home/dtd43/geckodriver')
driver.get("http://google.com/")
print ("Headless Firefox Initialized")
print(driver.title)
end_program_time = datetime.now()

print(end_program_time - start_program_time)
driver.quit()

