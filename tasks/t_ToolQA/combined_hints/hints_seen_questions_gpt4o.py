HINTS = {'step_by_step_tips': """Steps to Answer the Question:

1. Read the question carefully.
2. Choose appropriate tools. Read the documentation of the chosen tools to understand the functions of them.
3. Your final answer should be a string only containing the answers to the question without explanatory text.
""",

'specific_hint': """The following hints and example solution are provided to help you understand how to solve the question and use the tool. Please note that you will receive a new question, which will be different from the examples provided.

Hint: When solving the question by exploring the tabular database (airbnb, yelp, flights and coffee), remember to learn about the database by viewing the column names. Do not try to solve the task in one step. Break it down into smaller steps, and remember to print the result of each step.

Hint: How to calculate the distance between two points based on their latitude `lat_A`, `lat_B` and longitude `lon_A`, `lon_B`:
`distance = (lat_A - lat_B)**2 + (lon_A - lon_B)**2`

About Flight Identifier:
The flight identifier is a combination of the 'IATA_Code_Marketing_Airline' (a 2-letter code) and the 'Flight_Number_Marketing_Airline'.
For example:
IATA_Code_Marketing_Airline = 'G4', Flight_Number_Marketing_Airline = '567': 'G4567'
IATA_Code_Marketing_Airline = 'F9', Flight_Number_Marketing_Airline ='124': 'F9124'

Question: How many businesses are not open currently in Reno?
Hint: 
1. Filter the data based on the question. 
2. Get the value of 'is_open' for filtered rows into a variable `is_opens`.
3. `is_open_num = sum([1 for is_open in is_opens.split(', ') if is_open == '0'])`

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

Question: Which is the nearest Restaurants business to Perenn in Bay?
Solution:
1. Filter the data to get the row where 'name' is 'Perenn in Bay'. Then get the value of 'latitude' and 'longitude' of this row.
2. Keep only rows with 'categories' containing 'Restaurants'.
In this step, do not use the tool. Instead, use the following code:
`data_business = data[data['categories'].str.contains('Restaurants')]`
3. Get the value of 'latitude' and 'longitude' for Restaurants businesses into variables `lats` and `lons`.
4.
`lats_list = [float(lat) for lat in lats.split(', ')]`
`lons_list = [float(lon) for lon in lons.split(', ')]`
5. For each pair of latitude and longitude in lists, calculate the distance to 'Perenn in Bay'. Store the distance in a list `distances`.
6. Find the index of the minimum value in `distances`. Use the index to get the name. Do it strcitly as follows: `list(data_business['name'])[min_index]`.

Question: How many papers did Laddha write?
Hint:
1: Identify the co-author(s) of Laddha.
2: For each co-author, get their joint paper by checking the edge attributes.
3: Combine papers. Remember to remove duplicates.
4: Return the number of papers.

Question: How many papers did Laddha and Baran write together? / How many accumulated citations do papers collaborated by Laddha and Baran?
Hint: Check the edge attributes to find the papers jointly authored by Laddha and Baran. Remember to remove duplicates before counting the number of papers or calculating the total citations.

Question: Which is/are the most cited paper(s) written by Laddha?
Hint: 
First find out what papers Laddha wrote. Then check the citations of them.
If all papers by Laddha have zero citations, consider all of them as the most cited papers. 
Return only the title(s), without the number of citations.

Question: How many papers cited "A survey on Machine Learning"?
Hint: Focus only on the node attribute 'number of citations for this paper'. There is no need to know the title of papers that cited "A survey on Machine Learning".

Question: What is the total number of papers authored by Laddha and collaborators plus those written by collaborators and other people?
Hint:
1. Identify the co-author(s) of Laddha. (Answer: Baran).
2. For Laddha and Baran, get their joint paper by checking the edge attributes.
3. Find out additional co-authors of Baran.
4. Retrieve the papers jointly authored by Baran and each of Baran's additional co-authors.
5. Combine papers and remove duplicates to determine the total count.

Question: What institutions participated in the study of 'A survey on Machine Learning'?
Hint: Focus only on the node attribute of the paper 'A survey on Machine Learning'.
If there are multiple institutions, separate them with semicolon and space '; '.
If there is only one institution, provide only the name of the institution without semicolon added at the end.

Hint: Do not write '&' as '&amp'.

Hint: When camparing the citation count of papers, the same paper is only considered once.

Question: What is the postal code of Perenn in Bay in Troy, MO?
Hint: Filter the data to get the row where 'name' is 'Perenn in Bay', 'city' is 'Troy' and 'state' is 'MO'.

Question: What did Paul do on 2022/04/05 from 10:00 AM to 12:00 AM?
Hint: Start by retrieving, e.g., 10 documents. If you don't find the answer in the retrieved documents, try modifying your query by replacing keywords or rephrasing it, e.g., "Paul 2022/04/05 10:00 AM 12:00 AM"; "Paul' activities on 2022/04/05 from 10:00 AM to 12:00 AM"; "Paul's agenda on 2022/04/05 from 10:00 AM to 12:00 AM", etc.
You can also simplify your query by reducing the number of keywords, which help retrieve more results.
Provide the exact name of the event as stated in the document. For example, if the document indicates that the event is named 'park picnic', the answer should be 'park picnic' but not 'picnic'.

Hint: When a small number (e.g., 10) of documents are retrieved, remember to print them to manually go through the documents, instead of using too many programmatic solutions.
When a large number of documents are retrieved, it may not be feasible to display all of them at once, as the output could be truncated.

Hint: Dates in the documents are written in words. For example, '04/05' appear as 'April 5'.

Hint: Number of Documents to Retrieve: 
For questions about a specific time, place, event, or person, start with a smaller number of documents. If the answer is not found in the initial set, you can increase the number of documents retrieved.

Question: How long did Paul attend the Movie Party on 2022/01/01?
Start by retrieving, e.g., 10 documents. 
Provide the duration of the event in H:MM:SS. For example, if an event lasts 1 hours and 30 minutes, the answer should be '1:30:00'. If the event lasts 2 hours, the answer should be '2:00:00'."

Question: Who attended the exhibition?
Retrieved document: "The exhibition was planned by Paul, and he will host the event. He will present some art work then."
Solution: 
Start by retrieving, e.g., 10 documents. 
You only need to return one attendee's name. 
In this case, Paul is the host of the exhibition, which qualifies him as an attendee. Therefore, the answer is 'Paul'.

Question: When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2023/01/01?
This question is a more general one, which requires you to find out all events within a time window. For these types of question, you must follow the example solution below:
Solution:
1. Start by retrieving large number of documents related to Paul: `retrieved_docs = retrieve_agenda('Paul', 1000)`.
2. Do not print all retrieved documents. Keep only documents related to Paul: `docs_with_paul = [doc for doc in retrieved_docs if 'Paul' in doc]`. 
3. Filter documents that mention the date: `docs = [doc for doc in docs_with_paul if 'January 1' in doc]`. 
4. Print and read the retrieved documents, and think in your monologue to determine the answer. Avoid using programmatic solutions to extract the answer.
5.Seperate different time slots with a comma, e.g., '10:00 AM-12:00 PM, 2:00 PM-4:00 PM'.

Hint: To determine available time windows from 9:00 AM to 6:00 PM for a meeting:
1. Read the retrieved document carefully to identify event(s) between 9:00 AM and 6:00 PM. Focus on identifying any time slots where events conflict with the potential meeting time.
2. Use reasoning in your monologue to determine available time windows. The answer should be all time slots within 9:00 AM to 6:00 PM where no event is scheduled. 
    Note: Do not use programmatic solutions to calculate or extract the answer. Consider only available time windows within 9:00 AM to 6:00 PM. 
    Example:
    If an event is from 9:30 AM to 1:00 PM, the answer would be: 9:00 AM-9:30 AM, 1:00 PM-6:00 PM.
    If an event is from 4:00 PM to 6:00 PM, the answer would be: 9:00 AM-4:00 PM.
    If an event is from 7:00 AM to 10:00 AM, the answer would be: 10:00 AM-6:00 PM.
    If an event is from 6:00 PM to 7:00 PM, the answer would be: 9:00 AM-6:00 PM. (Events beyond the range of 9:00 AM to 6:00 PM should not affect the answer.)
3. Check your answer. If you are sure that your answer is correct in both value and format, you can call `complete_task(final_report: str, return_value)` to finish the task.

Question: On which date from 2010-01-15 to 2010-05-05 did the coffee price have the highest increase compared to the previous day?
Solution:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Get the value of 'Close' and 'Date' for each day into seperate variables: `close_prices` and `dates`.
3. Convert strings to lists:
`close_prices_list = [float(price) for price in close_prices.split(', ')]`
`dates_list = dates.split(', ')`
4. Calculate the price change for each day: `price_changes = [close_prices_list[i] - close_prices_list[i-1] for i in range(1, len(close_prices_list))]`.
5. Find the index of the maximum value in `price_changes`.
6. Get the date with the maximum price change.

Question: What was the percentage increase in coffee price from the start of 2010-01-15 to the end of 2010-05-05?
Hint:
You should compare the 'Close' price of '2010-05-05' with the 'Open' price of '2010-01-15'.

Question: How much did the coffee price change from the start of 'Day 1' to the end of 'Day 2'?
Hint:
1. Filter the data to get the row for 'Day 1' and the row for 'Day 2'.
2. Get the value of 'Open' for 'Day 1' and the value of 'Close' for 'Day 2'.
3. Calculate the price change: (value of 'Close' for 'Day 2' - value of 'Open' for 'Day 1').

Question: What was the average percentage change in coffee price from the start of 2010-01-15 to the end of 2010-05-05?
Hint:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' and 'Open' for each day.
3. For each day, calculate the percentage change: `percentage_change = (close_price - open_price) / open_price * 100`.
4. Calculate the average percentage change.

Question: On how many days from 2010-01-15 to 2010-05-05 did the coffee price close higher than the opening price?
Solution:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'Close' and 'Open' for each day into seperate variables: `close_prices` and `open_prices`.
3. Convert strings to lists:
`close_prices_list = [float(price) for price in close_prices.split(', ')]`
`open_prices_list = [float(price) for price in open_prices.split(', ')]`
4. Calculate the times of higher close price: `higher_close_times = sum([1 for i in range(len(close_prices_list)) if close_prices_list[i] > open_prices_list[i]])`.

Question: Can you recommend a Shared room with the lowest price within 10 miles radius from -74 longitude and 40 latitude?
Solution:
1. Calculate the maximum and minimum latitude and longitude within a 10 miles radius from the given point in the question into variables `max_lat`, `min_lat`, `max_lon`, `min_lon`.
2. Filter the data to get the row where 'room type' is 'Shared room'. Then get values of 'latitude', 'longitude', 'price' of filtered rows into variables `lats`, `lons`, `prices`.
3. ```# strcitly follow this
lats_list = [float(lat) for lat in lats.split(', ')]
lons_list = [float(lon) for lon in lons.split(', ')]
prices_list = [float(price) for price in prices.replace('$','').replace(',','').split()]```
4. Find the index of the minimum price, also within a 10 miles radius from the given point.
```
min_index = -1
for i in range(len(prices_list)):
    if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon):
        if min_index == -1 or prices_list[i] < prices_list[min_index]:
            min_index = i
```
5. Use the index to get the name from `filtered_db['NAME']`.
```

Question: What was the difference between the highest and the lowest coffee price from 2010-01-15 to 2010-05-05?
Hint:
1. Filter the data to get the rows from '2010-01-15' to '2010-05-05'.
2. Use the tool to get the value of 'High' and 'Low' for each day.
3. Calculate the difference between the maximum value of 'High' values and the minimum value of 'Low' values.
4. Remember to round the answer to the 1 decimal place using the `round()` function.

Question: What is the flight number of the Air Lines Inc. flight from CDC to EFE on 2020-01-01?
The answer must be (a sequence of) numerical code(s), e.g., '1400', or '1383, 2201'.
Remember to only provide the numerical code(s) without the flight 2-letter codes as the final answer.

Question: What is the fastest flight from CDC to EFE on Monday?
Solution:
1. Filter the data to get rows where 'Origin' is 'CDC', 'Dest' is 'EFE' and 'DayOfWeek' is '1'.
2. Get the value of 'AirTime', 'IATA_Code_Marketing_Airline', 'Flight_Number_Marketing_Airline' for filtered rows into seperate variables: `air_times`, `iata_codes`, `flight_numbers`.
3:
`air_times_list = [float(time) for time in air_times.split(', ')]`
`iata_codes_list = iata_codes.split(', ')`
`flight_numbers_list = flight_numbers.split(', ')`
4. Find the index of the minimum value in `air_times_list`.
5. Get the flight.

Question: What is the average flight time of AB123?
Hint:
1. Filter the data to get rows where 'IATA_Code_Marketing_Airline' is 'AB' and 'Flight_Number_Marketing_Airline' is '123'.
2. Get the value of 'AirTime' for filtered rows into a variable `air_times`.
3. Convert to a list of floating-point numbers: `air_times_list = [float(time) for time in air_times.split(', ')]`.
4. Remove the 'nan' values from the 'air_times_list': `air_times_list_nonnan = [time for time in air_times_list if time >= 0]`.
5. Calculate the average flight time. The answer should be a floating-point number with one decimal place.

Question: How long did AB123 delay when arrival on 2020-01-01?
Hint: You should get the value of 'ArrDelayMinutes'

Question: What is the average delay time of all the flights that departed from CDC on 2020-01-01?
Hint: You should get the value of 'DepDelayMinutes'.

Question: How long was the different between the CRS recorded departure time and actual departure time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'DepTime' and the value of 'CRSDepTime' into 'dep_time' and 'crs_dep_time'.
3. The final answer should be an interger: `int(float(crs_dep_time) - float(dep_time))`.

Question: How many extra minutes did the AB123 flight take from CDC to EFE on 2020-01-21?
Hint:
Get the answer by calculating the difference between the 'DepDelayMinutes' and the 'ArrDelayMinutes'.

Question: 
What was the local arrival time of the AB123 flight from CDC to EFE on 2020-01-01? / What was the CRS-recorded arrival time of the AB123 flight from CDC to EFE on 2020-01-01?
Hint:
1. Filter the data based on the question.
2. Get the value of 'ArrTime' / 'CRSArrTime' for the row into a variable `arr_time` / `crs_arr_time` / `dep_time`.
3. You must view the value by `print(arr_time)` / `print(crs_arr_time)`.
4. Convert the departure time into the 'HH:MM' format directly. For example:
- '820.0' becomes '8:20'.
- '1042.0' becomes '10:42'.

Question: How many flights were diverted on 2020-01-01?
Hint: Filter the data to get rows where 'Diverted' is 'True' and 'FlightDate' is '2020-01-01'.

Question: What is the total number of flights operated by XXX Airlines Inc. on 2020-01-01?
Hint: Filter the data to get rows where 'Airline' is 'XXX Airlines Inc.' and 'FlightDate' is '2020-01-01'.
Make sure to use the exact name of the airline as it appears in the question.
For example, for this question, you should filter with: 'Airline=XXX Airlines Inc.; FlightDate=2020-01-01'.

Question: What percentage of the flights from CLE were canceled 2020-01-01?
Hint: Filter the data to get rows where 'Origin' is 'CLE', 'FlightDate' is '2020-01-01' and Cancelled' is 'True'.

Hint: When answering questions about yelp data, remember to remove duplicates from the answer.

Question: How many days are Amazing MODERN Apartment in Prime Brooklyn available (id: 11111) during a year (365 days)?
Hint: Get the value of 'availability 365' and convert it to an integer as the final answer.

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

Hint: How to calculate maximum and minimum latitude and longitude within a `n` mile radius from a given point (latitude `target_lat`, longitude `target_lon`):
`import math`
`lat_offset = n / 69`
`lon_offset = n / (69 * math.cos(math.radians(lat)))`
`max_lat = target_lat + lat_offset
min_lat = target_lat - lat_offset
max_lon = target_lon + lon_offset
min_lon = target_lon - lon_offset` 

Question: Which city is Perenn in Bay located in Troy?
If there are multiple cities, separate them with a comma and a space ', '.
Remember to remove duplicates from the answer.

Question: What is the average price of airbnbs in Boerum?
Solution:
1. Filter the data to get rows where 'neighbourhood' is 'Boerum'.
2. Get the value of 'price' for filtered rows into a variable `prices`.
3. Convert `prices` to a list of floating-point numbers. Do it strcitly as follows: 
```prices_list = [float(price) for price in prices.replace('$','').replace(',','').split()]```
4. Calculate the average price. Use .format() to round the answer to the required decimal places.

Question: What are the hours of operation for Perenn in Bay in area with postal code 23444, Reno, MO?
After getting the answer from the tool, Use the exact output from the tool as the final answer, do not modify the format.

Question: How many Wedding Planning businesses are there in Reno, MO?
Solution:
1. Filter the data to get rows where 'city' is 'Reno' and 'state' is 'MO'.
2. Get the value of 'categories' for filtered rows into a variable `categories`.
3. Convert to a list of strings: `categories_list = categories.split(', ')`.
4. Calculate the number of Wedding Planning businesses: `num = sum([1 for bussiness in categories_list if 'Wedding Planning' in bussiness])`.

Question: What is the last review date of Amazing MODERN Apartment in "Astoria" (id: 2222) in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in "Astoria"', 'neighbourhood' is 'Bushwick' and 'id' is '2222'.
Get the value of 'last review' for the filtered row.

Question: Can you recommend a Restaurants business with the highest star rating within a 5-mile radius of 2278 Isla St?
Solution:
1. Filter the data to get the row where 'address' is '2278 Isla St'. Then get the value of 'latitude' and 'longitude' of this row.
2. Calculate the maximum and minimum latitude and longitude within a 5-mile radius from '2278 Isla St' into variables `max_lat`, `min_lat`, `max_lon`, `min_lon`.
3. Keep only rows with 'categories' containing 'Restaurants'.
In this step, do not use the tool. Instead, use the following code:
`data_business = data[data['categories'].str.contains('Restaurants')]`
4. Get the value of 'latitude', 'longitude', and 'stars' for Restaurants businesses into variables `lats`, `lons` and `stars`.
5.
`lats_list = [float(lat) for lat in lats.split(', ')]`
`lons_list = [float(lon) for lon in lons.split(', ')]`
`stars_list = [float(star) for star in stars.split(', ')]`
6. Find the index of the maximum star rating, also within a 5-mile radius from '2278 Isla St'.
```
max_index = -1
for i in range(len(stars_list)):
    if (lats_list[i]<=max_lat and lats_list[i] >= min_lat and lons_list[i] <= max_lon and lons_list[i] >= min_lon):
        if max_index == -1 or stars_list[i] > stars_list[max_index]:
            max_index = i
```
7. Use the index to get the name. Do it strcitly as follows: `list(data_business['name'])[max_index]`.

Question: What is the review rate number of Amazing MODERN Apartment in Prime Brooklyn in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn' and 'neighbourhood' is 'Bushwick'.
Note that the words after the last 'in' in the question indicates the 'neighbourhood'.
Use the exact phrasing from the question to filter the data.

Question: Is Perenn in Bay open in area with postal code 23444, Reno, MO?
The answer should be either 'Yes' or 'No'. 
If the value you get is '1', the answer shoud be 'Yes'; otherwise, the answer shoud be 'No'.

Question: Does Perenn in Bay require appointment in area with postal code 23444?
1. Get the value of 'attributes'.
2. Print the value.
3. Check if it contains 'ByAppointmentOnly'. If it does and 'ByAppointmentOnly' is 'True', the answer should be 'Yes'; if it does not or 'ByAppointmentOnly' is 'False', the answer should be 'No'.

Question: What is the host's name for Amazing MODERN Apartment in Prime Brooklyn in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn' and 'neighbourhood' is 'Bushwick'.
Note that the words after the last 'in' in the question indicates the 'neighbourhood'.
Use the exact phrasing from the question to filter the data.

Question: What is the average number of reviews per month of Amazing MODERN Apartment in Prime Brooklyn (id: 11111) in Bushwick?
Hint: Filter the data to get the row where 'NAME' is 'Amazing MODERN Apartment in Prime Brooklyn', 'neighbourhood' is 'Bushwick' and 'id' is '11111'. Do not fiter by other columns.
For this question, you do not need to format the answer. The value you get from the tool would be the final answer. 

Question: How many airbnbs are there in Bushwick?
Hint: Filter the data to get rows where 'neighbourhood' is 'Bushwick'. The number of these rows is the answer. 

Question: How much does it cost per night to stay at the most expensive entire home/apt in Bushwick?
Solution:
1. Filter the data to get rows where 'room type' is 'Entire home/apt' and 'neighbourhood' is 'Bushwick'.
2. Get the value of 'price' for filtered rows into a variable `prices`.
3. Convert `prices` to a list of floating-point numbers. Do it strcitly as follows: Do it strcitly as follows: 
```prices_list = [float(price) for price in prices.replace('$','').replace(',','').split()]```
4. Find the maximum value in `prices_list`. Ensure the final answer is in the correct format.

""",
# general hints
"generic_reasoning_tips": """Do not perform too many operations in a single cell.
Directly present the answer in the required format without programmatically converting the output.  
Note: Provide only the value of the answer as the final output, without any additional text or full sentences.
""",
"tool_tips": """When explore the tabular database, you can use the following tools: `load_db()`, `filter_db()`, and `get_value()`. Note that when using `filter_db()`, the column name and the value you provide should be exactly the same as what shown in the database and the question.
When explore the graph database, you can use the following tools: `load_graph()`, `check_nodes()`, `check_neighbours()` and `check_edges()`.
When explore the document database related to agenda, you can use the following tool: `retrieve_agenda()`.
Below is the documentation for each tool:
"""
}
