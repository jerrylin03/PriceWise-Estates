# PriceWise-Estates
A real estate investments web app. Utilizing data analysis, it offers insights into optimal price-to-rent ratios, notifies of new opportunities, and identifies undervalued houses in top school districts, aiding informed decisions and finds undervalued houses in top school districts.

Currently, PriceWise Estates CLI is a command-line interface (CLI) application designed to provide users with valuable insights into real estate properties, school districts, and investment opportunities. The application leverages external APIs and data sources to fetch and analyze relevant information.

## Features
1. **Fetch Properties:** Retrieve the newest 42 properties for sale in a specific state and city
2. **Fetch Top School Districts:** Obtain information about the top 10 school districts in a state, including district names, rank scores, and addresses.
3. **Filter Properties:** Allow users to filter properties based on their specified criteria, such as minimum and maximum price ranges. Display the filtered properties with additional investment metrics.
4. **User Profiles:** Enable users to create and update profiles with preferences related to real estate, school ratings, income, and expenses.
5. **Investment Metrics:** Calculate essential investment metrics for each property, including the price-to-rent ratio and mortgage payments, providing users with valuable insights into potential returns.
6. **External Data Parsing:** Parse external data sources, such as median rent, median price, mortgage rates, and projected growth. Store the parsed data in JSON format for future reference.

## Usage
- `python scanner_cli.py -function properties -state_code <state_code> -city <city>`: Fetch and store the newest properties for sale in a specific state and city.<br>
- `python scanner_cli.py -function filter -state_code <state_code> -city <city> -username <username>`: Filter properties based on user preferences and display investment metrics.<br>
- `python scanner_cli.py -function schools -state_code <state_code>`: Fetch and store information about the top school districts in a specific state.<br>
- `python scanner_cli.py -function profile -username <username>`: Create or update a user profile with real estate preferences.<br>
- `python scanner_cli.py -function parse`: Parse external data sources and store the data in JSON format.<be>

## Dependencies
- `requests`: Used for making HTTP requests to external APIs.<br>
- `dotenv`: Loads environment variables from a `.env` file.<br>
- `argparse`: Provides a command-line interface for user interaction.<br>

## License
Apache License
