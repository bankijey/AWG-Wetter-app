import pandas as pd
from awg import awg
from datetime import datetime
import pytz
import requests
import sys
import psycopg2
import config

# Load list of selected cities in South Africa
cities_df = pd.read_csv('SA_cities.csv', header=None)
cities_df.columns = ['ID', 'City', 'Latitude', 'Longitude']

# Initialise dataframe
weather_df = pd.DataFrame(columns=['City', 'Timestamp', 'Temperature', 'Pressure', 'Humidity', 'LPH', 'Compressor'])

# Set timezone for South Africa
tz_SA = pytz.timezone('Africa/Johannesburg')
time_SA = datetime.now(tz_SA).strftime("%d/%m/%Y %H:%M:%S")
api_key = config.api_token(api='openweathermap')
# Get weather information for selected cities from Openweathermap API
for city, lat, lon in zip(cities_df['City'], cities_df['Latitude'], cities_df['Longitude']):
    api_url = "http://api.openweathermap.org/data/2.5/weather?"
    payload = {'lat': lat, 'lon': lon, 'appid': api_key}
    response = requests.get(api_url, params=payload)  # Call the API using the get method and store the
    if response.ok:  # if all is well( no errors, no network timeouts)
        data = response.json()
        temp = round(data.get('main').get('temp') - 273.15, 3)
        pres = data.get('main').get('pressure')
        hum = data.get('main').get('humidity')
        # Compute the AWG performance from weather data
        lph, wcomp = awg(Tamb=temp, RH=hum / 100, Pres=pres * 100)
    else:
        temp, pres, hum, lph, wcomp = None   # Return none if the weather information of the particular location not found
    # Insert next line of data frame
    weather_df.loc[len(weather_df)] = [city, time_SA, temp, pres, hum, lph, wcomp]
weather_df = weather_df.convert_dtypes()
weather_df.to_csv('weather_df.csv', header=False, index = False)

#%% SAVE DATA ON SQL

conn = None
f = None

try:
    # connect to the PostgreSQL database
    params = config.db()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # Read csv file
    f = open('weather_df.csv', 'r')
    # Append data from csv file to database table
    cur.copy_from(f, 'weather', sep=",")
    conn.commit()

# Throw errors from SQL queries and/or file load
except psycopg2.DatabaseError as e:
    if conn:
        conn.rollback()
    print(f'Error {e}')
    sys.exit(1)

except IOError as e:
    if conn:
        conn.rollback()
    print(f'Error {e}')
    sys.exit(1)
# Close database connection and file
finally:
    if conn:
        conn.close()
    if f:
        f.close()