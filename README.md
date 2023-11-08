# API
Queries SOS API for taxa and observation data and stores it in a database for querying.

## Database Setup
1. Start your PostgreSQL service.
2. Create a new PostgreSQL database (if you already have, remove all tables from the database that are present in models.py as the script doesn't overwrite existing tables).
3. Set your database URL as an environment variable. Replace `username`, `password`, and `yourdatabase` with your PostgreSQL username, password, and the name of the database you created.

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
```

4. Run the setup.py to hopefully end up with a geodataframe containing observation counts per species, date and grid square. If it fails to run for some reason, you can try adding the git directory in the Python Path:

```bash
export PYTHONPATH=/[path_to_git_repo]/Ht23-Agilt-projektarbete:$PYTHONPATH
```

## TO DO
- Redo to do
- Recreate Pipfile (new environment and run needed installs)
- Make Bokeh work with Opendata API (caching/local storage)
    - Minimize querying of data (eg. no white tiles), is filtering possible?

## Notes
run_apps.py to start services
Image can be reached like so: http://127.0.0.1:5000/get_tile/5/17/9
