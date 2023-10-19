
## Changelog:

1. Changed class structure slightly so that my functions for calling the database wanted to work.
2. Added empty init.py files for python to recognize our folders as libraries to be imported from.
3. Created folder streamlit_functions with (as of right now) broken functions for creating layers dynamically which needs to be looked at by me at a future date when it's not 2:30 in the morning.
4. Made a few different methods for db.py for data handling and filter possibilities, including getting taxon id if we have a swedish name of a species, getting unique species for our dropdown search bar, and creating a pandas dataframe by using the queried, filtered data from our database. More work needs to be done in these and especially more troubleshooting from yours truly.
5. Created filtering options of start date of observations, end date of observations and name of the species.
6. Added a zoom-slider which does nothing at the moment because, you guessed it, layer creation doesn't work!

## Todo:
1. Troubleshooting every single function added.
2. Tidying up and figuring out why my layer creation doesn't want to work, but I suspect my session states and data handling procedures!
3. Make functions to handle GeoJSON data (and look into PostGIS in order to possibly use it there?)

