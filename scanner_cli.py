"""
scanner_cli.py

PriceWise Estates CLI
"""

import argparse
import json
import csv
import os
from dotenv import load_dotenv
from pip._vendor import requests

# To-DO
# Desgin document for refactor
# sqft
# bedroom
# price
# take ratio of all of them
# filter out to get first 5
# zillow/rentcast
# first version of investment score
# cash flow in output

# filter out 

# Load environment variables from .env file
load_dotenv()

RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def fetch_top_school_districts(state_code):
    """ Function to get the top 10 school districts in a state saved to a json file """
    api_url = os.getenv("SCHOOL_API_URL") + state_code

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": os.getenv("SCHOOL_API_HOST")
    }

    try:
        response = requests.get(api_url, headers=headers)

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

def fetch_properties(state_code, city):
    """ Function to get the newest 42 properties for sale by state and city saved to a json file """
    api_url = os.getenv("ESTATE_API_URL")

    querystring = {"state_code":state_code,"city":city, "sort":"newest","offset":"0"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": os.getenv("ESTATE_API_HOST")
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
    
        property_list =  response.json()["data"]["home_search"]["results"]

        file_name = "real_estate_for_sale_" + city + "_" + state_code + ".json"

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
                    "baths": property["description"]["baths"],
                    "sqft": property["description"]["sqft"]
                },
                "primary_photo": property["primary_photo"]
            }
            for property in property_list
        ]

        # Write to JSON
        with open(file_name, mode='w', encoding="utf-8") as file:
            json.dump(filtered_properties, file, indent=2)

        print(f"Retrieved newest 42 properties for sale in {city} {state_code} ")
        print(f"Saved to {file_name}")
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")

def property_pretty_output(real_property, state_code, city):
    """
    Format:
    $769,999
    4 bds | 3 ba | 2,938 sqft
    816 Anne St SW, Leesburg, VA 20175
    https://photos.zillowstatic.com/fp/39e4c06297eb6babfe6d0a0c1b477b7c-p_e.webp
    """
    metrics = calculate_metrics(real_property['property_id'], state_code, city)
    print(f"${real_property['list_price']}")
    print(f"Price to Rent Ratio: {metrics['price_to_rent_ratio']:.2f}")
    print(f"Mortgage Payments: ${metrics['mortgage_payments']:.2f}")
    print(f"{real_property['description']['beds']} bds | {real_property['description']['baths']} ba | {real_property['description']['sqft']} sqft")
    print(f"{real_property['address']['line']}, {real_property['address']['city']}, {real_property['address']['state_code']} {real_property['address']['postal_code']}")
    print(real_property['primary_photo']['href'])

def filter_properties(state_code, city, username):
    # Get profile filters from file
    with open("user_data.json", 'r', newline='', encoding='utf-8') as profile_file:
        user_data = json.load(profile_file)
    
    username_data = user_data[username]
    min_price = username_data['min_price_range']
    max_price = username_data['max_price_range']

    # Open properties file
    properties_file = "real_estate_for_sale_" + city + "_" + state_code + ".json"
    with open(properties_file, 'r', newline='', encoding='utf-8') as properties_file:
        properties_data = json.load(properties_file)

    # Iterate through property listings
    count = 1
    for real_property in properties_data:
        # Filter based on profile
        if real_property['list_price'] >= min_price and real_property['list_price'] <= max_price:      
            # Pretty output to terminal
            print(str(count) + ".")
            # TO-DO method call to calculate metrics/scores, output in dict, pass to pretty output
            property_pretty_output(real_property, state_code, city)
            print("-")
            count += 1

def parse_mortgage_file(input_file, output_file):
    # Parse mortgage file
    last_row = []

    # Parse zillow file
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Iterate through each row
        for row in reader:
            date = row['DATE']
            mortgage_rate = row['MORTGAGE30US']

            mortgage_data = {
                'date': date,
                'mortgage_rate': float(mortgage_rate)
            }

            # Update last_row with the current row
            last_row = mortgage_data

    # Save the parsed data in JSON format
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(last_row, jsonfile, indent=2)

    print(f"Parsed data saved to {output_file}")

def parse_zillow_file(input_file, output_file, data_name):
    data = []

    # Parse zillow file
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        region_data = {}

        for row in reader:
            # Grab the last key in the dict
            last_key = list(row)[-1]
            if row['RegionName'] != "United States":
                # Seperate region name into state and city
                city = row['RegionName'].split(", ")[0]
                state_code = row['RegionName'].split(", ")[1]
                
                if state_code in region_data:
                    region_data[state_code].update({
                        city: {data_name: row[last_key]}# Grab the most recent data column
                    })
                else:
                    region_data[state_code] = {
                        row['RegionName'].split(", ")[0]: {data_name: row[last_key]}
                    }

            data.append(region_data)

    # Save the parsed data in JSON format
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2)

    print(f"Parsed data saved to {output_file}")

def parse_external_data():
    """
    Parse data from 
    - median rent
    - median price
    - mortgage rates
    - projected growth
    store in JSON format

    Parameters:

    Returns:
    None: Saves the parsed data in JSON format.
    """

    parse_zillow_file(os.getenv("MEDIAN_RENT_FILE"), "median_rent_by_region.json", "median_rent")
    parse_zillow_file(os.getenv("MEDIAN_PRICE_FILE"), "median_price_by_region.json", "median_price")
    parse_zillow_file(os.getenv("FORECAST_GROWTH_FILE"), "projected_growth_by_region.json", "projected_growth")
    parse_mortgage_file(os.getenv("MORTGAGE_FILE"), "us_mortgage_rate.json")

def store_user_data(username):
    """
    Store and calculate metrics based on user data.

    Parameters:
    - username (str): Username of the user, used as a reference for stored values.

    Returns:
    None: Updates the json file user_data.json
    """
    # Load existing data from file

    update = "N"

    try:
        with open('user_data.json', 'r', encoding="utf8") as file:
            user_data = json.load(file)
        # Check if the username is already in the database
        if username in user_data:
            print(f"Hello, {username}!")
            # Print out current user profile
            username_data = user_data[username]
            print("Here is the current user profile")
            print(f"Real Estate Minimum Price: ${username_data['min_price_range']}")
            print(f"Real Estate Maximum Price: ${username_data['max_price_range']}")
            print(f"District Rating Preference: {username_data['school_rating_preference']}/10")
            print(f"Gross Monthly Income: ${username_data['gross_income']}")
            print(f"Monthly Debt Payments: ${username_data['current_debt']}")
            print(f"Management fees as percent of rental income: {username_data['management_fees']}%")
            print(f"Maintenance as percent of rental income: {username_data['maintenance_costs']}%")
            print(f"Insurance costs as percent of rental income: {username_data['insurance']}%")
            # Ask if we want to update
            update = input("Do you want to update the user profile ? (Y/N) ")
        else:
            print(f"New user {username}")
            update = "Y"
    except FileNotFoundError:
        # Create a new user_data dictionary if the file doesn't exist
        user_data = {}
        print(f"New user {username}")
        update = "Y"

    if update.upper() == "Y":
        # Ask for and save user input
        user_data[username] = {
            'min_price_range': float(input("Enter your minimum price $: ")),
            'max_price_range': float(input("Enter your maximum price $: ")),
            'school_rating_preference': int(input("Enter your school rating preference (1-10): ")),
            'gross_income': float(input("Enter your gross monthly income $: ")),
            'current_debt': float(input("Enter your current monthly debt payments $: ")),
            'management_fees': int(input("Enter management fees as percent of income: ")),
            'maintenance_costs': int(input("Enter maintenance costs as percent of income: ")),
            'insurance': int(input("Enter insurance costs as percent of rental income: "))
        }

        # Save the updated user data
        with open('user_data.json', 'w', encoding="utf8") as file:
            json.dump(user_data, file, indent=2)

        print(f"User data for {username} has been updated.")

def calculate_metrics(property_id, state_code, city):
    # Load data from JSON files
    with open("median_price_by_region.json", 'r', encoding='utf-8') as price_file:
        median_price_data = json.load(price_file)

    with open("median_rent_by_region.json", 'r', encoding='utf-8') as rent_file:
        median_rent_data = json.load(rent_file)

    # Get the specific fetched real estate file
    properties_file = "real_estate_for_sale_" + city + "_" + state_code + ".json"
    with open(properties_file, 'r', encoding='utf-8') as real_estate_file:
        real_estate_data = json.load(real_estate_file)

    # Mortgage Rates
    with open("us_mortgage_rate.json", 'r', encoding='utf-8') as mortgage_file:
        mortgage_rate_data = json.load(mortgage_file)

    # Find the property in real_estate_data using property_id
    property_info = None
    for info in real_estate_data:
        if info['property_id'] == property_id:
            property_info = info
            break

    # Extract state and city from the real estate data
    state = property_info['address']['state_code']
    city = property_info['address']['city']

    # Find the median price based on state and city
    median_price = None
    if state in median_price_data:
        city_data = median_price_data[state]
        if city in city_data:
            median_price = float(city_data[city]['median_price'])

    # Find median rent based on state and city
    median_rent = None
    if state in median_rent_data:
        city_data = median_rent_data[state]
        if city in city_data:
                median_rent = float(city_data[city]['median_rent'])
    
    # Calculate the price to rent ratio (need annual rent for formula)
    price_to_rent_ratio = median_price / (median_rent * 12)

    # Get Mortgage Payments
    # Assuming 30 Year mortgage with 80% of property value as principle
    # P(r/n) / (1 - (1 + (r/n) )^-nt )
    # Loan = P
    # Term 30 years = t
    # Mortgage Interest Rates = r
    # 12 = n
    p = property_info['list_price'] * 0.8
    t = 30
    n = 12
    r = mortgage_rate_data['mortgage_rate']/100
    payments = (p*(r/n))/(1-(1+(r/n))**(-(n*t)))

    return {"price_to_rent_ratio": price_to_rent_ratio, "mortgage_payments": payments}

    # Output the result
    # print(f"Property ID: {property_id}, State: {state}, City: {city}, Price to Rent Ratio: {price_to_rent_ratio:.2f}, Median Price: {median_price:.2f}, Median Annual Rent: {median_rent*12:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PriceWise Estates CLI")
    parser.add_argument("-function", help="Options: properties, districts, filter, profile, parse", required=True)
    parser.add_argument("-state_code", help="State code to fetch from, both properties & districts")
    parser.add_argument("-city",  help="City to fetch properties")
    parser.add_argument("-username", help="Used to reference stored user data", default="Guest")
    parser.add_argument("-property_id", help="Property id from real estate for sale")

    args = parser.parse_args()

    if args.function == "properties":
        fetch_properties(args.state_code, args.city)
    elif args.function == "filter":
        filter_properties(args.state_code, args.city, args.username)
    elif args.function == "schools":
        fetch_top_school_districts(args.state_code)
    elif args.function == "profile":
        store_user_data(args.username)
    elif args.function == "parse":
        parse_external_data()
    else:
        print("N/A, Options: properties, schools, profile")
