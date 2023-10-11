# Fenologik Proof of Concept
Streamlit app that pulls observations of birds from the [Species Observation System API](https://github.com/biodiversitydata-se/SOS) and plots it on a map.

## API
Script queries SOS API and pulls the first 100 observations of spotted nutcracker in the year 2023. It then stores it in a Pandas dataframe and saves the data to data.csv.

## Data handling and visualisation
Handled incoming .csv data from the API integration and organized the data using pandas functions in order to try to categorize the data further, in order to allow us to visually plot it using PyDeck functions which streamlit inherently favors.