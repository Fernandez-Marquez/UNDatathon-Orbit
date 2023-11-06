import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# To prevent spamming the service, we use RateLimiter to add delay between geocoding calls
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# The base URL of the API endpoint
base_url = "https://mymun.com/api/conferences"

# Parameters for the API request
params = {
    "filter_time": "future",
    "sb": "cd",
    "order": "asc",
    "per_page": 5,
    "online_conf": "false"
}

# Empty list to store all conference data
all_conferences = []

# Assume we do not know the total number of pages; we'll keep requesting until an empty response
current_page = 1

while True:
    # Set the current page
    params["page"] = current_page
    
    # Make the HTTP request to the API
    response = requests.get(base_url, params=params)
    
    # If the response is successful, no more results, break the loop
    if response.status_code != 200 or not response.json():
        break
    
    # Get the JSON data from the response
    data = response.json()
    
    # Add the data to the all_conferences list
    all_conferences.extend(data)
    
    # Increment the page number
    current_page += 1
    print("Parsing, getting next page")

# Now, for each conference, attempt to geocode the city to get coordinates
for conference in all_conferences:
    try:
        print("getting coordinates")
        # Use the geocode utility to find the location
        location = geocode(f"{conference['address_city']}, {conference['address_country']}")
        if location:
            conference['latitude'] = location.latitude
            conference['longitude'] = location.longitude
        else:
            conference['latitude'] = None
            conference['longitude'] = None
    except Exception as e:
        print(f"Error geocoding {conference['address_city']}: {e}")
        conference['latitude'] = None
        conference['longitude'] = None

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(all_conferences)

# Write the DataFrame to a CSV file with UTF-8 encoding
df.to_csv('conferences.csv', index=False, encoding='utf-8')

print(f"Data for {len(all_conferences)} conferences has been written to 'conferences.csv'")
