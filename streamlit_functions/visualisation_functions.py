import pydeck as pdk
import datetime

##################################################
#  - Functions for map visualisation creation -  #
##################################################

def get_date_from_string(date_string):
    if isinstance(date_string, datetime.date):
        # If it's already a date object, no conversion needed.
        return date_string
    try:
        # Otherwise, try to parse the string as expected.
        if not date_string.startswith("datetime.date"):
            raise ValueError(f"Invalid date string format: {date_string}")
        date_tuple = tuple(map(int, date_string.replace("datetime.date", "").strip("() ").split(", ")))
        return datetime.date(*date_tuple)
    except Exception as e:
        raise ValueError(f"Error processing date string {date_string}: {e}")
    
def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + datetime.timedelta(n)

def get_daily_data(species_id, start_date, end_date):
    date_list = list(daterange(start_date, end_date))
    daily_data = {
        index: {
            "species_id": species_id,
            "date": single_date.strftime('%Y-%m-%d')
        }
        for index, single_date in enumerate(date_list)
    }
    return daily_data

def get_daily_urls(daily_data):
    daily_urls = {
        index: f"http://localhost:3000/square_grid_obs/{{z}}/{{x}}/{{y}}?taxon_id={details['species_id']}&start_date={details['date']}&end_date={details['date']}"
        for index, details in daily_data.items()
    }
    return daily_urls

### WEEKLY ###

def get_weekly_urls(weekly_data):
    weekly_urls = {
        index: f"http://localhost:3000/square_grid_obs/{{z}}/{{x}}/{{y}}?taxon_id={details['species_id']}&start_date={details['start_date']}&end_date={details['end_date']}"
        for index, details in weekly_data.items()
    }
    print(weekly_urls)
    return weekly_urls

def get_weekly_data(species_id, start_date, end_date):
    date_list = [start_date + datetime.timedelta(days=7*n) for n in range(int((end_date - start_date).days/7) + 1)]
    weekly_data = {
        index: {
            "species_id": species_id,
            "start_date": single_date.strftime('%Y-%m-%d'),
            "end_date": (single_date + datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        }
        for index, single_date in enumerate(date_list)
    }
    print(weekly_data)
    return weekly_data



def get_tile_layer(data):
    return pdk.Layer(
        'TileLayer',
        data=data,
        opacity=0.5,
        filled=True,
    )


def get_grid_layer(data):
    return pdk.Layer(
        'MVTLayer',
        data=data,
        pickable=False,
        cell_size_pixels=20,
        get_fill_color="[128 + (properties.obs_count), 50 + (properties.obs_count / 50), 128 + (properties.obs_count / 50), (properties.obs_count) + 100]",
        getLineColor="[128 + (properties.obs_count), 50 + (properties.obs_count / 50), 128 + (properties.obs_count / 50), (properties.obs_count) + 150]",
        lineWidthMinPixels=1,
        get_position='[longitude, latitude]',
        get_weight='count'
    )