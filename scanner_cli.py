"""
scanner_cli.py

PriceWise Estates CLI
"""

import argparse
import csv
from pip._vendor import requests

def fetch_top_school_districts(state_code):
    """ Function to get the top 10 school districts in a state saved to a csv file """
    api_url = "https://schooldigger-k-12-school-data-api.p.rapidapi.com/v2.0/rankings/districts/VA"

    headers = {
        "X-RapidAPI-Key": "7816c75fadmshec207b26b80d79ep1b5b07jsnf5763b908667",
        "X-RapidAPI-Host": "schooldigger-k-12-school-data-api.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers)
        print(response.raise_for_status())

        district_list = response.json()["districtList"]

        file_name = "top_" + state_code + "_school_districts.csv"

        # Write to CSV
        with open(file_name, mode='w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["School District ID", "District Name", "Rank Score",
                             "Street", "City", "State Code", "Zip"])
            # Extract relevant information
            for district in district_list:
                district_data = [(district["districtID"],
                                district["districtName"],
                                district["rankHistory"][0]["rankScore"],
                                district["address"]["street"],
                                district["address"]["city"],
                                district["address"]["state"],
                                district["address"]["zip"])]
                writer.writerows(district_data)

        print(f"Gathered top school districts in {state_code}")
        print(f"Saved to {file_name}")
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")

def fetch_properties(state_code):
    """ Function to get the newest 42 properties for sale by state saved to a csv file """
    api_url = "https://us-real-estate.p.rapidapi.com/v3/for-sale"

    querystring = {"state_code":"VA","sort":"newest","offset":"0"}

    headers = {
        "X-RapidAPI-Key": "7816c75fadmshec207b26b80d79ep1b5b07jsnf5763b908667",
        "X-RapidAPI-Host": "us-real-estate.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        print(response.raise_for_status())

        property_list =  response.json()["data"]["home_search"]["results"]

        file_name = "real_estate_for_sale_" + state_code + ".csv"

        # Write to CSV
        with open(file_name, mode='w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Property ID", "Street", "City", "State Code", "Zip",
                            "List Price", "Bedrooms", "Bathrooms", "PhotoURL", "School DistrictID"])

            # Extract relevant information
            for single_property in property_list:
                property_data = [(single_property["property_id"],
                                single_property["location"]["address"]["line"],
                                single_property["location"]["address"]["city"],
                                single_property["location"]["address"]["state_code"],
                                single_property["location"]["address"]["postal_code"],
                                single_property["list_price"],
                                single_property["description"]["beds"],
                                single_property["description"]["baths"],
                                single_property["primary_photo"]["href"])]
                writer.writerows(property_data)

        print(f"Retrieved newest 42 properties for sale in {state_code}")
        print(f"Saved to {file_name}")
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PriceWise Estates CLI")
    parser.add_argument("-function", help="Function to use: properties, districts", required=True)
    parser.add_argument("-state_code", help="State code to fetch school districts", required=True)

    args = parser.parse_args()

    if args.function == "properties":
        fetch_properties(args.state_code)
    else:
        fetch_top_school_districts(args.state_code)
