import requests
import pandas as pd
import time


class ElectionDataFetcher:
    """
    Fetches and processes election result data from the UK Parliament data API.

    Attributes:
        base_url (str): The base URL for the election results API endpoint.
        election_data (DataFrame): Stores the combined election data.
    """

    def __init__(self):
        self.base_url = "https://lda.data.parliament.uk/electionresults.json"
        self.election_data = pd.DataFrame()

    def fetch_basic_results(self, page_size=100, page=0):
        """
        Fetches a single page of basic election results from the API.

        Parameters:
            page_size (int): Number of results per page.
            page (int): Page number to fetch.

        Returns:
            A list of basic election results if successful, None otherwise.
        """
        url = f"{self.base_url}?_view=Elections&_pageSize={page_size}&_page={page}"
        try:
            response = requests.get(url, timeout=5)  # Timeout after 5 seconds
            return (
                response.json()["result"]["items"]
                if response.status_code == 200
                else None
            )
        except requests.Timeout:
            print(f"Request timed out for page: {page}")
            return None

    def fetch_detailed_results(self, about_url):
        """
        Fetches detailed election results for a specific election ID.

        Parameters:
            about_url (str): The URL to fetch detailed results from.

        Returns:
            A dictionary of detailed election results if successful, None otherwise.
        """
        try:
            response = requests.get(about_url, timeout=5)
            return (
                response.json()["result"]["primaryTopic"]
                if response.status_code == 200
                else None
            )
        except requests.Timeout:
            print(f"Request timed out for URL: {about_url}")
            return None

    def process_results(self, max_pages=10, delay=1.0):
        """
        Processes a limited number of pages of election results.

        Parameters:
            max_pages (int): Maximum number of pages to process.
            delay (float): Delay between API calls to avoid rate limiting.
        """
        for page in range(max_pages):
            basic_results = self.fetch_basic_results(page_size=100, page=page)
            if not basic_results:
                break

            temp_data = []
            for item in basic_results:
                id = item["_about"].rsplit("/", 1)[-1]
                detailed_url = (
                    f"https://lda.data.parliament.uk/electionresults/{id}.json"
                )
                detailed_result = self.fetch_detailed_results(detailed_url)

                if detailed_result:
                    election_info = self.extract_election_info(detailed_result)
                    candidate_data = self.extract_candidate_data(detailed_result)
                    for _, candidate_row in candidate_data.iterrows():
                        merged_row = {**election_info, **candidate_row}
                        temp_data.append(merged_row)

            self.election_data = pd.concat(
                [self.election_data, pd.DataFrame(temp_data)], ignore_index=True
            )
            time.sleep(delay)

    def extract_election_info(self, detailed_result):
        """
        Extracts relevant information from a detailed election result.

        Parameters:
        - detailed_result (dict): A dictionary containing detailed information about an election result.

        Returns:
        dict: A dictionary containing extracted information, including:
            - "constituency": The label of the constituency.
            - "election": The label of the election.
            - "electorate": The total number of electorates.
            - "majority": The majority obtained in the election.
            - "result_of_election": The result of the election.
            - "turnout": The turnout percentage in the election.
        """
        return {
            "constituency": detailed_result["constituency"]["label"]["_value"],
            "election": detailed_result["election"]["label"]["_value"],
            "electorate": detailed_result["electorate"],
            "majority": detailed_result["majority"],
            "result_of_election": detailed_result["resultOfElection"],
            "turnout": detailed_result["turnout"],
        }

    def extract_candidate_data(self, detailed_result):
        """
        Extracts relevant candidate data from a detailed election result.

        Parameters:
        - detailed_result (dict): A dictionary containing detailed information about candidates in an election.

        Returns:
        pandas.DataFrame: A DataFrame containing extracted candidate information, including:
            - "name": The full name of the candidate.
            - "votes": The number of votes received by the candidate.
            - "party": The political party affiliation of the candidate.
        """
        candidate_data = pd.DataFrame(detailed_result["candidate"])
        candidate_data = candidate_data[["fullName", "numberOfVotes", "party"]]
        candidate_data["name"] = candidate_data["fullName"].apply(lambda x: x["_value"])
        candidate_data["votes"] = candidate_data["numberOfVotes"]
        candidate_data["party"] = candidate_data["party"].apply(
            lambda x: x["_value"] if "_value" in x else None
        )
        return candidate_data[["name", "votes", "party"]]

    def save_to_csv(self, file_name):
        """
        Saves election data to a CSV file.

        Parameters:
        - file_name (str): The name of the CSV file to which the election data will be saved.
        """
        self.election_data.to_csv(file_name, index=False)
        print(f"Data saved to {file_name}")
