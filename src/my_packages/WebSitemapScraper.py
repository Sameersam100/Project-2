import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class WebSitemapScraper:
    """
    A class to scrape, process, and export sitemap URLs from a given base website.

    Attributes:
        base_url (str): The base URL of the website to scrape.
        sitemaps_frames (dict): A dictionary to store the sitemap URLs and their corresponding DataFrames.
    """

    def __init__(self, base_url):
        """
        Initializes the WebSitemapScraper with a base URL and starts collecting sitemaps.

        Parameters:
            base_url (str): The base URL of the website to scrape.
        """
        self.base_url = base_url
        self.sitemaps_frames = {}
        self.collect_sitemaps()

    def retrieve_web_data(self, endpoint):
        """
        Retrieves web content from a given endpoint with custom headers.

        Parameters:
            endpoint (str): The URL to fetch the content from.

        Returns:
            str: The content retrieved from the endpoint, or an empty string if an error occurs.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
            }

            result = requests.get(endpoint, headers=headers)
            result.raise_for_status()
            return result.text

        except requests.exceptions.RequestException as error:
            print(f"Error during web request: {error}")
            return ""

    def process_sitemap(self, url_of_sitemap):
        """
        Processes a given sitemap URL by fetching and parsing its XML content.
        Recursively processes nested sitemaps and stores the results in sitemaps_frames.

        Parameters:
            url_of_sitemap (str): The URL of the sitemap to be processed.
        """
        sitemap_xml = self.retrieve_web_data(url_of_sitemap)
        parser = BeautifulSoup(sitemap_xml, "xml")
        links = []

        for location in parser.find_all("loc"):
            links.append(location.text)
            if location.text.endswith(".xml"):
                self.process_sitemap(location.text)
        identifier = url_of_sitemap.split("/")[-1]
        dataframe = pd.DataFrame(links, columns=["Links"])
        dataframe = self.process_links(dataframe)
        self.sitemaps_frames[identifier] = dataframe

    def collect_sitemaps(self):
        """
        Collects and processes all sitemaps listed in the website's robots.txt file.
        """
        robots_content = self.retrieve_web_data(f"{self.base_url}/robots.txt")

        for line in robots_content.split("\n"):
            if line.startswith("Sitemap:"):
                sitemap_link = line.split(": ")[1].strip()
                self.process_sitemap(sitemap_link)

    def process_links(self, data_frame):
        """
        Processes a DataFrame of URLs by extracting and adding subdirectory levels as new columns.

        Parameters:
            data_frame (DataFrame): A DataFrame containing URLs to be processed.

        Returns:
            DataFrame: The modified DataFrame with added columns for subdirectories.
        """
        url_prefix = "https://www.datacamp.com/"
        maximum_depth = 0

        def split_url(link):
            if link.startswith(url_prefix):
                return link[len(url_prefix) :].strip("/").split("/")
            else:
                return [None]

        for idx, record in data_frame.iterrows():
            subdir_levels = split_url(record["Links"])
            maximum_depth = max(maximum_depth, len(subdir_levels))
            data_frame.loc[
                idx, ["subdir" + str(j + 1) for j in range(len(subdir_levels))]
            ] = subdir_levels

        for depth in range(maximum_depth):
            column_name = "subdir" + str(depth + 1)
            if column_name not in data_frame.columns:
                data_frame[column_name] = None

        return data_frame

    def export_to_csv(self, folder="sitemaps"):
        """
        Exports all the sitemaps DataFrames to CSV files in a specified folder.

        Parameters:
            folder (str): The folder where the CSV files will be saved.
        """
        if not os.path.isdir(folder):
            os.mkdir(folder)

        for map_url, frame in self.sitemaps_frames.items():
            file_name = map_url + ".csv"
            file_path = os.path.join(folder, file_name)
            frame.to_csv(file_path, index=False)
