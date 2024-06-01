import requests
import csv

def get_scheme_data(scheme_code):
    url = f"https://www.rupeevest.com/home/get_mf_portfolio_tracker?schemecode={scheme_code}"
    try:
        print(f"Fetching data for scheme code: {scheme_code}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something went wrong", err)
    return None

def extract_data(json_data):
    if not json_data:
        return []

    fund_info = json_data.get("fund_info", [])
    stock_data = json_data.get("stock_data", [])

    extracted_data = []
    for fund in fund_info:
        for stock_entry in stock_data:
            for stock in stock_entry:
                entry = {
                    "s_name": fund.get("s_name", ""),
                    "aumdate": fund.get("aumdate", ""),
                    "aumtotal": fund.get("aumtotal", ""),
                    "fincode": stock.get("fincode", ""),
                    "invdate": stock.get("invdate", ""),
                    "noshares": stock.get("noshares", ""),
                    "percent_aum": stock.get("percent_aum", ""),
                }
                extracted_data.append(entry)

    return extracted_data

def main():
    # Read scheme codes from MFCodes.csv
    with open('MFCodes.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        scheme_codes = [row['schemecode'] for row in reader]

    # Fetch data for each scheme code and store in a list
    data_list = []
    for scheme_code in scheme_codes:
        scheme_data = get_scheme_data(scheme_code)
        if scheme_data:
            extracted_data = extract_data(scheme_data)
            data_list.extend(extracted_data)

    # Write the collected data to a CSV file
    with open('output_data.csv', 'w', newline='') as csvfile:
        fieldnames = ["s_name", "aumdate", "aumtotal", "fincode", "invdate", "noshares", "percent_aum"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in data_list:
            writer.writerow(entry)

    print("Script completed. Data written to output_data.csv.")

    # Dictionary to keep track of the first occurrence of fincode for each mutual fund scheme
    unique_fincode_per_scheme = {}

    # Filter and keep only the first occurrence of fincode for each mutual fund scheme
    filtered_data_list = []
    for entry in data_list:
        scheme_fincode_key = (entry["s_name"], entry["fincode"])
        if scheme_fincode_key not in unique_fincode_per_scheme:
            # First occurrence, add to the filtered list and update the dictionary
            filtered_data_list.append(entry)
            unique_fincode_per_scheme[scheme_fincode_key] = True

    # Write the filtered data to a CSV file
    with open('output_data_filtered.csv', 'w', newline='') as csvfile:
        fieldnames = ["s_name", "aumdate", "aumtotal", "fincode", "invdate", "noshares", "percent_aum"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in filtered_data_list:
            writer.writerow(entry)

    print("Script completed. Filtered data written to output_data_filtered.csv.")

if __name__ == "__main__":
    main()
