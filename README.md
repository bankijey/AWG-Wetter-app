# AWG-Wetter-app
App to compare Atmospheric Water Generator performance based on current weather conditions in different cities. The ‘awg.py’ function models the air Dehumidification process. 

Currently, the code is provisioned to run locally in a development environment. I used Windows Task Scheduler to run the program hourly and save data on a PostgreSQL database on my local machine. I would be creating a PowerBI dashboard with this data.

Future changes include:
1.	Building a production app on Heroku, Azure and/or AWS
2.	Modifying the cities database to go beyond South Africa ( would definitely require more resources)
3.	Improving the Capability of the ‘awg.py’ functions
4.	Creating a DASH dashboard with proper frontend styling.
