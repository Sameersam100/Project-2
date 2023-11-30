import requests
from bs4 import BeautifulSoup
import pandas as pd

"""
National Parks Data Scraping Module

This module contains the NationalParksScraper class that allows for scraping
data from a national parks listing webpage. The class is designed to extract
information about national parks in the United States, including names, descriptions,
images, locations, top experiences, best times to visit, and guide links.

The scraper fetches the HTML content from the provided URL, parses it using BeautifulSoup
to extract relevant information, and organizes the data into a pandas DataFrame. The 
DataFrame can then be saved to a CSV file for further use.

Classes:
    NationalParksScraper: A scraper for US national parks data from a travel website.

Methods:
    fetch_data: Sends a GET request to the provided URL and retrieves the webpage content.
    parse_data: Parses the HTML content and extracts data of interest.
    extract_park_info: Extracts the detailed information of each park from a div element.
    to_dataframe: Converts the list of dictionaries containing parks data into a DataFrame.
    save_to_csv: Saves the DataFrame to a CSV file.
    run: Executes the scraping process by invoking the fetch_data and parse_data methods.

Example:
    scraper = NationalParksScraper(url="https://www.earthtrekkers.com/us-national-parks-list/#allparks")
    national_parks_df = scraper.run()
    scraper.save_to_csv("national_parks.csv")

This module requires the requests and beautifulsoup4 libraries to be installed within the Python
environment you are running this script in.

Note:
    The scraping is limited to the structure of the webpage at the time of writing this script.
    Any changes to the webpage's structure may require updates to the scraping logic.
"""


class NationalParksScraper:
    """Web scraper for extracting information about parks from a specified URL and storing the data."""
    def __init__(self, url):
        """Initialize the ParksScraper instance with the given URL."""

        self.url = url
        self.parks_data = []

    def fetch_data(self):
        """Fetch data from the specified URL and return a BeautifulSoup object."""

        response = requests.get(self.url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            raise Exception("Failed to retrieve the webpage")

    def parse_data(self, soup):
        """Parse data from the BeautifulSoup object, extracting information about parks."""

        required_classes = {"x-section", "m138k-0", "m138k-1", "m138k-3"}

        def has_required_classes(tag):
            return tag.name == "div" and required_classes.issubset(
                set(tag.get("class", []))
            )

        target_divs = soup.find_all(has_required_classes)[
            2:65
        ]  

        for div in target_divs:
            park_info = self.extract_park_info(div)
            self.parks_data.append(park_info)

    def extract_park_info(self, div):
        """Extract park information from a given div element and return a dictionary."""

        park_info = {}

        park_info["Park Name"] = div.find("h4", class_="h-custom-headline").get_text(
            strip=True
        )
        park_info["Description"] = div.find("div", class_="x-text").get_text(strip=True)

        image_tag = div.find("img")
        park_info["Image URL"] = (
            image_tag["data-src"] if "data-src" in image_tag.attrs else image_tag["src"]
        )

        for p in div.find_all("p"):
            text = p.get_text(strip=True)
            if "Location:" in text:
                park_info["Location"] = text.split(":", 1)[1].strip()
            elif "Top Experiences:" in text:
                park_info["Top Experiences"] = text.split(":", 1)[1].strip()
            elif "When to Go:" in text:
                park_info["Best Time to Visit"] = text.split(":", 1)[1].strip()

        guide_link_tag = div.find("a", href=True)
        park_info["Guide Link"] = guide_link_tag["href"] if guide_link_tag else None

        return park_info

    def to_dataframe(self):
        """Convert the scraped park data to a pandas DataFrame."""

        return pd.DataFrame(self.parks_data)

    def save_to_csv(self, filename):
        """Save the scraped park data to a CSV file with the specified filename."""

        df = pd.DataFrame(self.parks_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def run(self):
        """Run the scraper, fetching and parsing data, and return the result as a DataFrame."""
        soup = self.fetch_data()
        self.parse_data(soup)
        return self.to_dataframe()
