from dataclasses import asdict
from tasks.base import BaseTask
from agent.agent import Agent
from .utils.utils import normalize_answer, basic_normalize_answer
from .init_script import construct_init_script
from .format_tips import FORMAT_TIPS


def modify_agent(agent: Agent):
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")
    agent.workspace.add_variables({"complete_task" : agent.core_tools.complete_task})
    agent.workspace.add_variables({"data_filter" : agent.core_tools.data_filter})
    agent.workspace.add_variables({"get_value" : agent.core_tools.get_value})
    agent.workspace.add_variables({"load_db" : agent.core_tools.load_db})

task_descriptions = """In this task, you are asked to answer a question via retrieving relevant information from a database (`pandas.DataFrame`). You can use provided tools to assist in exploring the database. You should return a string as the final answer.

Here is the question:
"""

step_by_step_tips = """Steps to Answer the Question:

1. Read the question carefully.
2. Load the relevant database.
3. Understand what kinds of information are stored in the database by viewing column names.
4. Retrieve the information that is asked in the question by using the provided tools.
5. Your final answer should be a string only containing the answers to the question without explanatory text.
"""

answer_tip = """Note: Provide only the value of the answer as the final output, without any additional text or full sentences.
"""

# question-specific hints
# ------------------------
# coffee
hint_coffee_print = """Before ending the task, print the final answer to check the value and the format of it.
"""
hint_coffee_price_change = """Hint on solution:
Question: How much did the coffee price change from the start of 'Day 1' to the end of 'Day 2'?
Hint:
1. Filter the data to get the row for 'Day 1' and the row for 'Day 2'.
2. Get the value of 'Open' for 'Day 1' and the value of 'Close' for 'Day 2'.
3. Calculate the price change: (value of 'Close' for 'Day 2' - value of 'Open' for 'Day 1').
"""
hint_coffee_highest_increase = """To answer this question, you must follow the example solution below:
Question: On which date from 2010-01-15 to 2010-05-05 did the coffee price have the highest increase compared to the previous day?
Solution:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' and 'Date' for each day into seperate variables: `close_prices` and `dates`.
3. Convert strings to lists:
`close_prices_list = [float(price) for price in close_prices.split(', ')]`
`dates_list = dates.split(', ')`
4. Calculate the price change for each day: `price_changes = [close_prices_list[i] - close_prices_list[i-1] for i in range(1, len(close_prices_list))]`.
5. Find the index of the maximum value in `price_changes`: `max_index = price_changes.index(max(price_changes))`.
6. Get the date with the maximum price change: `dates_list[max_index + 1]`.
"""
hint_coffee_increase_times = """To answer this question, you must follow the example solution below:
Question: How many times from 2010-01-15 to 2010-05-05 did the coffee price increase compared to the previous day?
Solution:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' for each day into `close_prices`.
3. Convert strings to lists:
`close_prices_list = [float(price) for price in close_prices.split(', ')]`
4. Calculate the times of price increase:
'price_increase_times = sum([1 for i in range(1, len(close_prices_list)) if close_prices_list[i] > close_prices_list[i-1]])'.
"""
hint_coffee_percentage_increase = """Hint on solution:
Question: What was the percentage increase in coffee price from the start of 2010-01-15 to the end of 2010-05-05?
Hint:
You should compare the 'Close' price of '2010-05-05' with the 'Open' price of '2010-01-15'.
"""
hint_coffee_percentage_change = """Hint on solution:
Question: What was the average percentage change in coffee price from the start of 2010-01-15 to the end of 2010-05-05?
Hint:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' and 'Open' for each day.
3. For each day, calculate the percentage change: `percentage_change = (close_price - open_price) / open_price * 100`.
4. Calculate the average percentage change.
"""
hint_coffee_higher_close_price = """To answer this question, you must follow the example solution below:
Question: On how many days from 2010-01-15 to 2010-05-05 did the coffee price close higher than the opening price?
Solution:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' and 'Open' for each day into seperate variables: `close_prices` and `open_prices`.
3. Convert strings to lists:
`close_prices_list = [float(price) for price in close_prices.split(', ')]`
`open_prices_list = [float(price) for price in open_prices.split(', ')]`
4. Calculate the times of higher close price: `higher_close_times = sum([1 for i in range(len(close_prices_list)) if close_prices_list[i] > open_prices_list[i]])`.
"""
hint_coffee_price_range = """Hint on solution:
Question: What was the difference between the highest and the lowest coffee price from 2010-01-15 to 2010-05-05?
Hint:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'High' and 'Low' for each day.
3. Calculate the difference between the maximum value of 'High' values and the minimum value of 'Low' values.
4. Remember to round the answer to the 1 decimal place using the `round()` function.
"""
hint_coffee_bullish_or_bearish = """Hint on solution:
Question: Was 2010-01-15 a bearish or bullish day for coffee price?
Solution: Compare the close price with the open price of the same day mentioned in the question.
"""

# flights
hint_round = """Use `.format()` to round the answer to the required decimal places if needed.
"""
hint_flights_deptime = """Hint on solution:
Question: What was the departure time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'DepTime' for the row (e.g.,'1234.0') into a variable `dep_time`.
3. You must view the value by `print(dep_time)`.
4. Convert the departure time into the 'HH:MM' format directly. For example:
- '840.0' becomes '8:40'.
- '1842.0' becomes '18:42'.

Note: Do not programmatically convert the value. Instead, directly write the answer in the correct 'HH:MM' format.
"""
hint_flights_difftime = """Hint on solution:
Question: How long was the different between the CRS recorded departure time and actual departure time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'DepTime' and the value of 'CRSDepTime' into 'dep_time' and 'crs_dep_time'.
3. The final answer should be an interger: `int(float(crs_dep_time) - float(dep_time))`.
"""
hint_flights_number = """
The flight identifier is a combination of the 'IATA_Code_Marketing_Airline' (a 2-letter code) and the 'Flight_Number_Marketing_Airline'.
For example:
IATA_Code_Marketing_Airline = 'G4', Flight_Number_Marketing_Airline = '567': 'G4567'
IATA_Code_Marketing_Airline = 'F9', Flight_Number_Marketing_Airline ='124': 'F9124'
"""
hint_flights_extramin = """Hint on solution:
Questions: How many extra minutes did the AB123 flight take from CDC to EFE on 2020-01-21?
Hint:
Get the answer by calculating the difference between the 'DepDelayMinutes' and the 'ArrDelayMinutes'.
"""
hint_flights_arrtime = """Hint on solution:
Question: What was the local arrival time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'ArrTime' for the row (e.g.,'820.0') into a variable `arr_time`.
3. You must view the value by `print(arr_time)`.
4. Convert the departure time into the 'HH:MM' format directly. For example:
- '820.0' becomes '8:20'.
- '1042.0' becomes '10:42'.

Note: Do not programmatically convert the value. Instead, directly write the answer in the correct 'HH:MM' format.
"""
hint_flights_crstime = """Hint on solution:
Question: What was the CRS-recorded arrival time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'CRSArrTime' for the row (e.g.,'820.0') into a variable `crs_arr_time`.
3. You must view the value by `print(crs_arr_time)`.
4. Convert the departure time into the 'HH:MM' format directly. For example:
- '820.0' becomes '8:20'.
- '1042.0' becomes '10:42'.

Note: Do not programmatically convert the value. Instead, directly write the answer in the correct 'HH:MM' format.
"""
hint_flights_airtime = """Hint on solution:
Question: How long was the flight time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint: Get the value of 'AirTime'. Print the value you get.
Convert it to a string representing an interge as the answer: `str(int(float(flight_time)))`
"""
hint_flights_taxin = """ Hint on solution:
Question: How many minutes did the AB123 flight take to taxi in on 2020-01-01?
Hint:
1. Filter the data to get the row where 'IATA_Code_Marketing_Airline' is 'AB', 'Flight_Number_Marketing_Airline' is '123' and 'FlightDate' is '2020-01-01'.
2. Get the value of 'TaxiIn' for the row (e.g.,'5.0') into a variable `taxi_in`.
3. You must view the value by `print(taxi_in)`.
4. Convert the answer into a string representing an interge, e.g., '5'.
"""
hint_flights_diverted = """Hint on solution:
Question: How many flights were diverted on 2020-01-01?
Hint: Filter the data to get rows where 'Diverted' is 'True' and 'FlightDate' is '2020-01-01'.
"""
hint_flights_distance = """To answer this question, you must follow the example solution below:
Question: How many flights with a distance greater than 300 miles on 2020-01-01?
Solution:
1. Filter the data to get rows where 'FlightData' is '2020-01-01'.
2. Get the value of 'Distance' for filtered rows into a variable `distances`.
3. Convert to a list of floating-point numbers: `distances_list = [float(dist) for dist in distances.split(', ')]`.
4. Calculate the number of flights with a distance greater than 300 miles: `num = sum([1 for i in range(len(distances_list)) if distances_list[i] > 300.0])`.
"""
hint_flights_avgairtime = """Hint on solution:
Question: What is the average air time of flights from CDC to EFE host by Air Lines Inc?
Hint:
1. Filter the data with 'Origin' as 'CDC', 'Dest' as 'EFE' and 'Airline' as 'Air Lines Inc'. Make sure to use the exact name of the airline as it appears in the question
2. Get the value of 'AirTime' for filtered rows into a variable `air_times`.
3. Convert to a list of floating-point numbers: `air_times_list = [float(time) for time in air_times.split(', ')]`.
4. Remove the 'nan' values from the 'air_times_list': `air_times_list_nonnan = [time for time in air_times_list if time >= 0]`.
5. Calculate the average air time: `avg_air_time = sum(air_times_list_nonnan) / len(air_times_list_nonnan)`.
"""
hint_flights_unique = """To answer this question, you must follow the example solution below:
Question: How many unique flights from CDC to EFE host by Air Lines Inc?
Solution:
1. Filter the data to get rows where 'Origin' is 'CDC', 'Dest' is 'EFE' and 'Airline' is 'Air Lines Inc'. Make sure to use the exact name of the airline as it appears in the question.
2. Get the value of 'Flight_Number_Marketing_Airline' for filtered rows into a variable `flight_numbers`.
3. Convert to a list of strings: `flight_numbers_list = flight_numbers.split(', ')`.
4. Calculate the number of unique flights: `num = len(set(flight_numbers_list))`.
"""
hint_flights_avgtime = """Hint on solution:
Question: What is the average flight time of AB123?
Hint:
1. Filter the data to get rows where 'IATA_Code_Marketing_Airline' is 'AB' and 'Flight_Number_Marketing_Airline' is '123'.
2. Get the value of 'AirTime' for filtered rows into a variable `air_times`.
3. Convert to a list of floating-point numbers: `air_times_list = [float(time) for time in air_times.split(', ')]`.
4. Remove the 'nan' values from the 'air_times_list': `air_times_list_nonnan = [time for time in air_times_list if time >= 0]`.
5. Calculate the average flight time. The answer should be a floating-point number with one decimal place.
"""
hint_flights_fastest = """To answer this question, you must follow the example solution below:
Question: What is the fastest flight from CDC to EFE on Monday?
Solution:
1. Filter the data to get rows where 'Origin' is 'CDC', 'Dest' is 'EFE' and 'DayOfWeek' is '1'.
2. Get the value of 'AirTime', 'IATA_Code_Marketing_Airline', 'Flight_Number_Marketing_Airline' for filtered rows into seperate variables: `air_times`, `iata_codes`, `flight_numbers`.
3:
`air_times_list = [float(time) for time in air_times.split(', ')]`
`iata_codes_list = iata_codes.split(', ')`
`flight_numbers_list = flight_numbers.split(', ')`
4. Find the index of the minimum value in `air_times_list`: `min_index = air_times_list.index(min(air_times_list))`.
5. Get the flight: `iata_codes_list[min_index]+flight_numbers_list[min_index]`
"""
hint_flights_avgspeed = """To answer this question, you must follow the example solution below:
Question: What is the average speed of AB123 from CDC to EFE (miles per minute)?
Solution:
1. Filter the data to get rows where 'IATA_Code_Marketing_Airline' is 'AB', 'Flight_Number_Marketing_Airline' is '123', 'Origin' is 'CDC' and 'Dest' is 'EFE'.
2. Get the value of 'Distance' and 'AirTime' for filtered rows into seperate variables: `distances`, `air_times`.
3. Convert to lists of floating-point numbers:
`distances_list = [float(dist) for dist in distances.split(', ')]`
`air_times_list = [float(time) for time in air_times.split(', ')]`
4. Remove both the 'nan' values from the 'air_times_list', and corresponding values in 'distances_list':
`air_times_list_nonnan = [air_times_list[i] for i in range(len(air_times_list)) if air_times_list[i] >= 0]`
`distances_list_nonnan = [distances_list[i] for i in range(len(air_times_list)) if air_times_list[i] >= 0]`
5. Calculate the average speed: `avg_speed =sum(distances_list_nonnan) / sum(air_times_list_nonnan)`. 
"""
hint_flights_totalnumber = """Hint on solution:
Question: What is the total number of flights operated by XXX Airlines Inc. on 2020-01-01?
Hint: Filter the data to get rows where 'Airline' is 'XXX Airlines Inc.' and 'FlightDate' is '2020-01-01'.

Make sure to use the exact name of the airline as it appears in the question.
For example, for this question, you should filter with: 'Airline=XXX Airlines Inc.; FlightDate=2020-01-01'.
"""
hint_flights_cancelled = """Hint on solution:
Question: What percentage of the flights from CLE were canceled 2020-01-01?
Hint: Filter the data to get rows where 'Origin' is 'CLE', 'FlightDate' is '2020-01-01' and Cancelled' is 'True'.
"""
# yelp
hint_yelp_print = """After getting the value of a column, remember to print it to view the value."""
hint_yelp_unique_name = """Use the exact output from the tool as the final answer, ensuring duplicates are removed.
For example:
'AZ, AZ': the final answer is 'AZ'
'Tampa, Brandon, Eagle, Tampa': the final answer is 'Tampa, Brandon, Eagle'
"""
hint_yelp_postal_code = """Hint on solution:
Question: What is the postal code of Perenn in Bay in Troy, MO?
Hint: Filter the data to get the row where 'name' is 'Perenn in Bay', 'city' is 'Troy' and 'state' is 'MO'.
"""
hint_yelp_star_rating = """Hint on solution:
Question: What is the star rating of Perenn in Bay in area with postal code 23444, Reno, MO?
Hint: Filter the data to get the row where 'name' is 'Perenn in Bay', 'postal_code' is '23444', 'city' is 'Reno' and 'state' is 'MO'.
"""
hint_yelp_hrs_operation = """Hint on solution:
After getting the answer from the tool, Use the exact output from the tool as the final answer, do not modify the format.
For example:
'Monday: 0:0-0:0, Tuesday: 7:0-17:0, Wednesday: 11:0-22:0': the final answer is 'Monday: 0:0-0:0, Tuesday: 7:0-17:0, Wednesday: 11:0-22:0'.
"""
hint_yelp_coordinates = """Hint on solution: 
Question: What are the coordinates of Perenn in Bay in area with postal code 12345, Reno, MO?
Filter the data to get the row where 'name' is 'Perenn in Bay', 'postal_code' is '12345', 'city' is 'Reno' and 'state' is 'MO'.
"""
hint_yelp_num_business = """"To answer this question, you must follow the example solution below:
Question: How many Wedding Planning businesses are there in Reno, MO?
Solution:
1. Filter the data to get rows where 'city' is 'Reno' and 'state' is 'MO'.
2. Get the value of 'categories' for filtered rows into a variable `categories`.
3. Convert to a list of strings: `categories_list = categories.split(', ')`.
4. Calculate the number of Wedding Planning businesses: `num = sum([1 for bussiness in categories_list if 'Wedding Planning' in bussiness])`.
"""
hint_yelp_highest_rating = """To answer these two questions, you must follow the example solution below:
Question: Which Restaurants business has the highest star rating / highest review count in Reno, MO?
Solution:
1. Filter the data to get rows where 'city' is 'Reno' and 'state' is 'MO'.
2. Keep only filtered rows with 'categories' containing 'Restaurants'. 
In this step, do not use the tool. Instead, use the following code:
`data_business = data[data['categories'].str.contains('Restaurants')]`
3. Get the value of 'stars' or 'review_count' for filtered rows into seperate variables: `stars`, `review_counts`.
4. 
`stars_list = [float(star) for star in stars.split(', ')]`
`review_counts_list = [int(review_count) for review_count in review_counts.split(', ')]`
5. Find the index of the maximum value in `stars_list`/`review_counts_list`. Use the index to get the name: `list(data_business['name'])[max_index]`.
"""
hint_yelp_distance = """How to calculate the distance between two points based on their latitude `lat_A`, `lat_B` and longitude `lon_A`, `lon_B`:
`distance = (lat_A - lat_B)**2 + (lon_A - lon_B)**2`
"""
hint_yelp_radius = """How to calculate maximum and minimum latitude and longitude within a 5-mile radius from a given point (latitude `target_lat`, longitude `target_lon`):
`import math`
`lat_offset = 5 / 69`
`lon_offset = 5 / (69 * math.cos(math.radians(lat)))`
`max_lat = target_lat + lat_offset
min_lat = target_lat - lat_offset
max_lon = target_lon + lon_offset
min_lon = target_lon - lon_offset`
"""
hint_yelp_avg_review = """To answer this question, you must follow the example solution below:
Question: What is the average review counts of businesses within a 5-mile radius from Perenn in Bay?
Solution:
1. Filter the data to get the row where 'name' is 'Perenn in Bay'. Then get the value of 'latitude' and 'longitude' of this row.
2. Calculate the maximum and minimum latitude and longitude within a 5-mile radius from 'Perenn in Bay' into variables `max_lat`, `min_lat`, `max_lon`, `min_lon`.
3. Get the value of 'latitude', 'longitude' and 'review_count' for all businesses into variables `lats`, `lons` and `review_counts`.
4. 
`lats_list = [float(lat) for lat in lats.split(', ')]`
`lons_list = [float(lon) for lon in lons.split(', ')]`
`review_counts_list = [int(review_count) for review_count in review_counts.split(', ')]`
5. keep only the review counts of businesses within a 5-mile radius from 'Perenn in Bay':
`review_counts_within_5 = [review_counts_list[i] for i in range(len(review_counts_list)) if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon)]`
6. Calculate the average review counts. Make sure the final answer is in a correct format.
"""
hint_yelp_nearest_business = """To answer this question, you must follow the example solution below:
Question: Which is the nearest Restaurants business to Perenn in Bay?
Solution:
1. Filter the data to get the row where 'name' is 'Perenn in Bay'. Then get the value of 'latitude' and 'longitude' of this row.
2. Keep only rows with 'categories' containing 'Restaurants'. In this step, do not use the tool. Instead, use the following code:
`data_business = data[data['categories'].str.contains('Restaurants')]`
3. Get the value of 'latitude' and 'longitude' for Restaurants businesses into variables `lats` and `lons`.
4.
`lats_list = [float(lat) for lat in lats.split(', ')]`
`lons_list = [float(lon) for lon in lons.split(', ')]`
5. For each pair of latitude and longitude in lists, calculate the distance to 'Perenn in Bay'. Store the distance in a list `distances`.
6. Find the index of the minimum value in `distances`. Use the index to get the name. Do it strcitly as follows: `list(data_business['name'])[min_index]`.
"""
hint_yelp_recommendation = """To answer this question, you must follow the example solution below:
Question: Can you recommend a Restaurants business with the highest star rating within a 5-mile radius of 2278 Isla St?
Solution:
1. Filter the data to get the row where 'address' is '2278 Isla St'. Then get the value of 'latitude' and 'longitude' of this row.
2. Calculate the maximum and minimum latitude and longitude within a 5-mile radius from '2278 Isla St' into variables `max_lat`, `min_lat`, `max_lon`, `min_lon`.
3. Keep only rows with 'categories' containing 'Restaurants'. In this step, do not use the tool. Instead, use the following code:
`data_business = data[data['categories'].str.contains('Restaurants')]`
4. Get the value of 'latitude', 'longitude', and 'stars' for Restaurants businesses into variables `lats`, `lons` and `stars`.
5.
`lats_list = [float(lat) for lat in lats.split(', ')]`
`lons_list = [float(lon) for lon in lons.split(', ')]`
`stars_list = [float(star) for star in stars.split(', ')]`
6. Find the index of the maximum star rating, also within a 5-mile radius from '2278 Isla St':
```
max_index = -1
for i in range(len(stars_list)):
    if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon):
        if max_index == -1 or stars_list[i] > stars_list[max_index]:
            max_index = i
```
7. Use the index to get the name. Do it strcitly as follows: `list(data_business['name'])[max_index]`.
"""
hint_yelp_open = """Hint on solution:
Question: How many businesses are not open currently in Reno?
Hint: 
1. Filter the data by 'city'.
2. Get the value of 'is_open' for filtered rows into a variable `is_opens`.
3. 
`is_open_num = sum([1 for is_open in is_opens.split(', ') if is_open == '0'])`
"""
hint_yelp_avg_star_rating = """Hint on solution:
Question: What is the average star rating of Food businesses in Reno?
Hint: 
1. Filter the data to get rows where 'city' is 'Reno'.
2. Keep only filtered rows with 'categories' containing 'Food'. In this step, do not use the tool. Instead, use the following code: `data_food = data[data['categories'].str.contains('Food')]`.
3. Calculate the average star rating. Make sure the final answer is in a correct format.
"""
hint_yelp_open_yes_no = """The answer should be either 'Yes' or 'No'. 
If the value you get is '1', the answer shoud be 'Yes'; otherwise, the answer shoud be 'No'.
"""
hint_yelp_appointment_yes_no = """Hint on solution:
1. Get the value of 'attributes'.
2. Print the value.
3. Check if it contains 'ByAppointmentOnly'. If it does and 'ByAppointmentOnly' is 'True', the answer should be 'Yes'; if it does not or 'ByAppointmentOnly' is 'False', the answer should be 'No'.
Note that determining the answer only requires checking the value of 'ByAppointmentOnly'. Other attributes, e.g., 'RestaurantsReservations' should not be considered.
"""

# airbnb
hint_airbnb_format = """
Before completing the task, you must print the value you get to recheck the format of the answer to ensure it is correct.
"""
hint_airbnb_host_name = """Hint on solution:
Question: What is the host's name for Amazing MODERN Apartment in Prime Brooklyn in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn' and 'neighbourhood' is 'Bushwick'.
Note that the words after the last 'in' in the question indicates the 'neighbourhood', and the words before the last 'in' indicates the 'NAME'.
Use the exact phrasing from the question to filter the data.
"""
hint_airbnb_available_days = """Hint on solution:
Question: How many days are Amazing MODERN Apartment in Prime Brooklyn available (id: 11111) during a year (365 days)?
Hint: Get the value of 'availability 365' and convert it to an integer as the final answer.
"""
hint_airbnb_review_rate = """Hint on solution:
Question: What is the review rate number of Amazing MODERN Apartment in Prime Brooklyn in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn' and 'neighbourhood' is 'Bushwick'.
Note that the words after the last 'in' in the question indicates the 'neighbourhood'.
Use the exact phrasing from the question to filter the data.
"""
hint_airbnb_last_review_date = """Hint on solution:
Question: What is the last review date of Amazing MODERN Apartment in "Astoria" (id: 2222) in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in "Astoria"', 'neighbourhood' is 'Bushwick' and 'id' is '2222'.
Get the value of 'last review' for the filtered row.
"""
hint_airbnb_avg_review = """Hint on solution:
Question: What is the average number of reviews per month of Amazing MODERN Apartment in Prime Brooklyn (id: 11111) in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn', 'neighbourhood' is 'Bushwick' and 'id' is '11111'. Do not fiter by other columns.
For this question, you do not need to format the answer. The value you get from the tool would be the final answer. 
"""
hint_airbnb_num = """Hint on solution:
Question: How many airbnbs are there in Bushwick?
Hint: Filter the data to get rows where 'neighbourhood' is 'Bushwick'. The number of these rows is the answer. 
"""
hint_airbnb_avg_price = """To answer this question, you must follow the example solution below:
Question: What is the average price of airbnbs in Boerum?
Solution:
1. Filter the data to get rows where 'neighbourhood' is 'Boerum'.
2. Get the value of 'price' for filtered rows into a variable `prices`.
3. Convert `prices` to a list of floating-point numbers. Do it strcitly as follows: 
```prices = prices.replace('$','').replace(',','')
prices_list = [float(price) for price in prices.split()]```
4. Calculate the average price. Use .format() to round the answer to the required decimal places.
"""
hint_airbnb_cost_per_night = """To answer this question, you must follow the example solution below:
Question: How much does it cost per night to stay at the most expensive entire home/apt in Bushwick?
Solution:
1. Filter the data to get rows where 'room type' is 'Entire home/apt' and 'neighbourhood' is 'Bushwick'.
2. Get the value of 'price' for filtered rows into a variable `prices`.
3. Convert `prices` to a list of floating-point numbers. Do it strcitly as follows: Do it strcitly as follows: 
```prices = prices.replace('$','').replace(',','')
prices_list = [float(price) for price in prices.split()]```
4. Find the maximum value in `prices_list`. Ensure the final answer is in the correct format.
"""
hint_airbnb_high_rate = """
Question: How many airbnbs are there in Bushwick that have a review rate not lower than 4?
Solution: Strcitly follow the example solution below: 
Get the value of 'review rate number', and convert each value to a float. Then, count the number of values that are not lower than 4:
`num = sum([1 for rate in rates.split(', ') if float(rate)>=4])`.
"""
hint_airbnb_radius = """How to calculate maximum and minimum latitude and longitude within a 10 miles radius from a given point (latitude `target_lat`, longitude `target_lon`):
`import math`
`lat_offset = 10 / 69`
`lon_offset = 10 / (69 * math.cos(math.radians(lat)))`
`max_lat = target_lat + lat_offset
min_lat = target_lat - lat_offset
max_lon = target_lon + lon_offset
min_lon = target_lon - lon_offset`
"""
hint_airbnb_lowest_price = """To answer this question, you must follow the example solution below:
Can you recommend me a hotel room with the lowest price in Bushwick?
Solution:
1. Filter the data to get rows where 'neighbourhood' is 'Bushwick'.
2. Get the value of 'price' for filtered rows into a variable `prices`.
3. Convert `prices` to a list of floating-point numbers. Do it strcitly as follows: 
```prices = prices.replace('$','').replace(',','')
prices_list = [float(price) for price in prices.split()]```
4. Find the index of the minimum value in `prices_list`. Use the index to get the name. Do it strcitly as follows: `list(filtered_db['NAME'])[min_index]`.
"""
hint_airbnb_recommendation = """To answer this question, you must follow the example solution below:
Question: Can you recommend a Shared room with the lowest price within 10 miles radius from -74 longitude and 40 latitude?
Solution:
1. Calculate the maximum and minimum latitude and longitude within a 10 miles radius from the given point in the question into variables `max_lat`, `min_lat`, `max_lon`, `min_lon`.
2. Filter the data to get the row where 'room type' is 'Shared room'. Then get values of 'latitude', 'longitude', 'price' of filtered rows into variables `lats`, `lons`, `prices`.
3. ```# strcitly follow this
lats_list = [float(lat) for lat in lats.split(', ')]
lons_list = [float(lon) for lon in lons.split(', ')]
prices = prices.replace('$','').replace(',','')
prices_list = [float(price) for price in prices.split()]```
4. Find the index of the minimum price, also within a 10 miles radius from the given point:
```
min_index = -1
for i in range(len(prices_list)):
    if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon):
        if min_index == -1 or prices_list[i] < prices_list[min_index]:
            min_index = i
```
5. Use the index to get the name. Do it strcitly as follows: `list(filtered_db['NAME'])[min_index]`.
"""

# ------------------------

class TableTask(BaseTask):
   
    def __init__(self, question_answer, db_variant = 'flights', question_variant = 0, level = 'easy', custom_init_script = False, basic_normalization = True):
        self.question_variant = question_variant
        self.db_variant = db_variant
        self.level = level
        self.task_question = question_answer[0][question_variant]
        self.task_question_type = question_answer[2][question_variant]
        self.task_answer = question_answer[1][question_variant]
        self.return_cls_name = "str" #"TaskAnswer" 
        self.task = task_descriptions + self.task_question + "\n\nFormat tip: " + FORMAT_TIPS[self.db_variant][self.task_question_type]
        # self.init_script = construct_init_script(custom_init_script, level, db_variant, self.task_question_type)
        self.budget = 20
        self.apply_basic_normalization = basic_normalization

    def evaluate(self, agent, verbose = False):
        "Produce the score and report, as well as fill out analytics"
        score, report = (1.0, "")
        self.analytics = {
            "log_path" : agent.run_path / "output.ans",
            "data_variant" : self.question_variant,
        }
        issue = ''
        # agent_answer_dict = asdict(agent.return_value)
        # agent_answer_type = list(agent_answer_dict.keys())[0]
        # agent_answer = agent_answer_dict.get(agent_answer_type, None)
        agent_answer = agent.return_value
        true_answer = self.task_answer
        if not isinstance(true_answer, str):
            true_answer = str(true_answer)
        if not isinstance(agent_answer, str):
            agent_answer = str(agent_answer)

        if self.apply_basic_normalization:
            if_correct = basic_normalize_answer(agent_answer, true_answer, self.level, self.db_variant, self.question_variant)
        else:
            if_correct = normalize_answer(agent_answer, true_answer, self.level, self.db_variant, self.task_question_type)

        if not if_correct:
            issue += f'Incorrect Answer: {agent_answer}; Expected: {true_answer}'
            score = 0.0
        else:
            issue += 'Correct Answer'

        self.analytics["score"] = score

        report += f"score: {score:.2f}\n\n" + f"Issues:{issue}"

        return score, report

    @classmethod
    def generate_variants(cls, question_answer: tuple, db_variant: str = 'flights', level: str = 'easy', custom_init_script: bool = False, basic_normalization: bool = True, question_index: int = 0, number_of_questions: int = 100):
        return [
            cls(question_answer, db_variant, question_variant, level, custom_init_script, basic_normalization)
            for question_variant in range(question_index, question_index + number_of_questions)
        ]

    @property
    def default_name(self):
        name = f"t_table_task_{self.db_variant}_{self.level}_v{self.question_variant}"
        return name
