import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures

# URL of the World Bank data page
url = "https://data.worldbank.org/country"

# Send a GET request to the URL
response = requests.get(url)


def fetch_country_data(country_url):
    try:
        country_response = requests.get(country_url)
        if country_response.status_code == 200:
            country_soup = BeautifulSoup(country_response.content, "html.parser")

            # Extract population
            population = "N/A"
            population_tag = country_soup.find('a', href=True, string="Population, total")
            if population_tag:
                population_value_tag = population_tag.find_next('div', class_='indicator-item__data-info')
                if population_value_tag:
                    population = population_value_tag.get_text(strip=True)

            # Extract life expectancy
            life_expectancy = "N/A"
            life_expectancy_tag = country_soup.find('a', href=True, string="Life expectancy at birth, total (years)")
            if life_expectancy_tag:
                life_expectancy_value_tag = life_expectancy_tag.find_next('div', class_='indicator-item__data-info')
                if life_expectancy_value_tag:
                    life_expectancy = life_expectancy_value_tag.get_text(strip=True)

            return (population, life_expectancy)
        else:
            return ("N/A", "N/A")
    except Exception as e:
        print(f"Error fetching data for {country_url}: {e}")
        return ("N/A", "N/A")


# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the relevant data in the HTML
    countries = []
    country_urls = []

    # Extract country names and URLs
    country_tags = soup.select('a[href*="/country/"]')
    for tag in country_tags:
        country_name = tag.get_text(strip=True)
        country_url = "https://data.worldbank.org" + tag.get('href')
        countries.append(country_name)
        country_urls.append(country_url)

    # Use ThreadPoolExecutor to fetch country data concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_country_data, country_urls))

    populations, life_expectancies = zip(*results)

    # Create a DataFrame to store the data
    country_data = pd.DataFrame({
        "Country": countries,
        "Population": populations,
        "Life_Expectancy": life_expectancies
    })

    # Save the DataFrame to a CSV file
    country_data.to_csv("world_bank_country_data.csv", index=False)
    print("Data saved to world_bank_country_data.csv")
else:
    print("Failed to retrieve the data")

