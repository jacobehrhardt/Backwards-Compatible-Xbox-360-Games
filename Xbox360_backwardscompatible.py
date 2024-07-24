from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import time
import csv

# Function to get the backward compatible games list from the Xbox website
def get_backward_compatible_games():
	url = 'https://www.xbox.com/en-ca/games/backward-compatibility?cat=xbox360'

	# Set up Selenium with headless Chrome
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--no-sandbox")

	# Initialize the WebDriver
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
	driver.get(url)

	game_list = []

	while True:
		try:
			# Wait for the games section to be present
			WebDriverWait(driver, 20).until(
				EC.presence_of_all_elements_located((By.CLASS_NAME, 'm-product-placement-item'))
			)

			# Get the page source and parse it with BeautifulSoup
			soup = BeautifulSoup(driver.page_source, 'html.parser')

			# Find the list of backward compatible games
			games_section = soup.find_all('div', class_='m-product-placement-item')

			# Debugging: Print the number of games found
			print(f"Number of games found: {len(games_section)}")

			if games_section:
				for game in games_section:
					game_name_tag = game.find('h3', class_='c-subheading-4')
					price_tag = game.find('span', class_='textpricenew x-hidden-focus')
					if game_name_tag:
						game_name = game_name_tag.text.strip()
						game_price = price_tag.text.strip() if price_tag else "N/A"
						if game_name not in game_list:
							game_list.append((game_name, game_price))
							# Debugging: Print each game name and price as it is found
							print(f"Found game: {game_name}, Price: {game_price}")

			# Check if there is a "Next" button to go to the next page
			try:
				next_button = WebDriverWait(driver, 10).until(
					EC.element_to_be_clickable((By.XPATH, '//a[@aria-label="Next Page"] | //li[@class="paginatenext"]//a[@aria-label="Next Page"] | //span[text()="Next"]'))
				)
				print("Next button found, clicking it.")
				next_button.click()
				time.sleep(5)  # Wait for the next page to load
			except Exception as e:
				print("No more pages or error navigating to the next page:", e)
				break

		except Exception as e:
			print(f"Error occurred: {e}")
			break

	driver.quit()
	return game_list

# Function to save the games list to a CSV file
def save_games_to_csv(games, filename='backward_compatible_games.csv'):
	with open(filename, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(['Game Title', 'Price'])
		for game in games:
			writer.writerow([game[0], game[1]])

# Get the list of backward compatible games
backward_compatible_games = get_backward_compatible_games()

# Save the list of backward compatible games to a CSV file
save_games_to_csv(backward_compatible_games)

# Print the list of backward compatible games using PrettyTable
table = PrettyTable()
table.field_names = ["Backward Compatible Xbox 360 Games", "Price"]
for game, price in backward_compatible_games:
	table.add_row([game, price])

print(table)

# Print the total count of games
print(f"Total games found: {len(backward_compatible_games)}")