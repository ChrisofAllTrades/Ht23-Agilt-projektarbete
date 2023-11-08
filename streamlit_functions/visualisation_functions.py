import pydeck as pdk

##################################################
#  - Functions for map visualisation creation -  #
##################################################

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
        opacity=0.8,
        get_position='[longitude, latitude]',
        get_weight='count'
    )



def get_geojson_layer(data):
    return pdk.Layer(
        'GeoJsonLayer',
        data=data,
        opacity=0.4,
        stroked=False,
        filled=True,
        extruded=False,
        wireframe=True,
    )


