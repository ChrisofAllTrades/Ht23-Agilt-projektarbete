# API
Queries SOS API for taxa and observation data and stores it in a database for querying.

## Database Setup
1. Start your PostgreSQL service.
2. Create a new PostgreSQL database.
3. Set your database URL as an environment variable. Replace `username`, `password`, and `yourdatabase` with your PostgreSQL username, password, and the name of the database you created.

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
```

4. Seed the taxa table and manually set id column to not NULL and primary key, and scientificName to not NULL in pgAdmin
5. Run the Python script to create the tables in your database.

NOTE! Before seeding the observations table, you need to run the following query in pgAdmin:

```SQL
ALTER TABLE observations 
ALTER COLUMN id 
SET DEFAULT nextval('observations_id_seq');
```

It adds an automatic sequencer to the id column since it's lacking in the data. If it's missing, the script will try to import it into the id column and will throw an error.

## TO DO
- Recreate Pipfile (new environment and run needed installs)
- Make Bokeh work with Opendata API (caching/local storage)
    - Minimize querying of data (eg. no white tiles), is filtering possible?

## Notes
run_apps.py to start services
Image can be reached like so: http://127.0.0.1:5000/get_tile/5/17/9
