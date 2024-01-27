"""
scanner_cli.py

PriceWise Estates CLI
"""

import argparse
import json
import csv
from pip._vendor import requests

API_KEY = ""

def fetch_top_school_districts(state_code):
    """ Function to get the top 10 school districts in a state saved to a json file """
    api_url = "https://schooldigger-k-12-school-data-api.p.rapidapi.com/v2.0/rankings/districts/VA"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "schooldigger-k-12-school-data-api.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers)
        print(response.raise_for_status())

        district_list = response.json()["districtList"]

        file_name = "top_" + state_code + "_school_districts.json"

        # Extract specific information from each district
        filtered_districts = [
            {
                "districtName": district["districtName"],
                "rankScore": district["rankHistory"][0]["rankScore"],
                "address": {
                    "street": district["address"]["street"],
                    "city": district["address"]["city"],
                    "state": district["address"]["state"],
                    "zip": district["address"]["zip"]
                }
            }
            for district in district_list
        ]

        # Write to JSON
        with open(file_name, mode='w', encoding="utf-8") as file:
            json.dump(filtered_districts, file, indent=2)

        print(f"Gathered top school districts in {state_code}")
        print(f"Saved to {file_name}")
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")

def fetch_properties(state_code):
    """ Function to get the newest 42 properties for sale by state saved to a json file """
    api_url = "https://us-real-estate.p.rapidapi.com/v3/for-sale"

    querystring = {"state_code":"VA","sort":"newest","offset":"0"}

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "us-real-estate.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        print(response.raise_for_status())

        property_list =  response.json()["data"]["home_search"]["results"]

        file_name = "real_estate_for_sale_" + state_code + ".json"

        # Extract specific information from each property
        filtered_properties = [
            {
                "property_id": property["property_id"],
                "address": {
                    "line": property["location"]["address"]["line"],
                    "city": property["location"]["address"]["city"],
                    "state_code": property["location"]["address"]["state_code"],
                    "postal_code": property["location"]["address"]["postal_code"]
                },
                "list_price": property["list_price"],
                "description": {
                    "beds": property["description"]["beds"],
                    "baths": property["description"]["baths"]
                },
                "primary_photo": property["primary_photo"]
            }
            for property in property_list
        ]

        # Write to JSON
        with open(file_name, mode='w', encoding="utf-8") as file:
            json.dump(filtered_properties, file, indent=2)

        print(f"Retrieved newest 42 properties for sale in {state_code}")
        print(f"Saved to {file_name}")
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")

def store_user_data(username):
    """
    Store and calculate metrics based on user data.

    Parameters:
    - username (str): Username of the user, used as a reference for stored values.

    Returns:
    None: Updates the json file user_data.json
    """
    # Load existing data from file
    try:
        with open('user_data.json', 'r', encoding="utf8") as file:
            user_data = json.load(file)
    except FileNotFoundError:
        # Create a new user_data dictionary if the file doesn't exist
        user_data = {}

    # Check if the username is already in the database
    if username in user_data:
        print(f"Hello, {username}!")
    else:
        print(f"New user {username}")

    # Ask for and save user input
    user_data[username] = {
        'min_price_range': float(input("Enter your minimum price $: ")),
        'max_price_range': float(input("Enter your maximum price $: ")),
        'school_rating_preference': int(input("Enter your school rating preference (1-5): ")),
        'gross_income': float(input("Enter your gross income $: ")),
        'current_debt': float(input("Enter your current debt $: ")),
        'property_management_fees': float(input("Enter property management fees %: ")),
        'maintenance_costs': float(input("Enter maintenance costs: ")),
        'property_taxes': float(input("Enter property taxes: ")),
        'insurance': float(input("Enter insurance costs: "))
    }

    # Save the updated user data
    with open('user_data.json', 'w', encoding="utf8") as file:
        json.dump(user_data, file, indent=2)

    print(f"User data for {username} has been updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PriceWise Estates CLI")
    parser.add_argument("-function", help="Options: properties, districts, forms", required=True)
    parser.add_argument("-state_code", help="State code to fetch from, both properties & districts ")
    parser.add_argument("-city",  help="City to fetch properties")
    parser.add_argument("-username", help="Used to reference stored user data", default="Guest")

    args = parser.parse_args()

    if args.function == "properties":
        fetch_properties(args.state_code)
    elif args.function == "schools":
        fetch_top_school_districts(args.state_code)
    elif args.function == "forms":
        store_user_data(args.username)
    else:
        print("N/A, Options: properties, schools, forms")
