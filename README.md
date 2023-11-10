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

5. Run this in the query tool in pgAdmin to add the square_grid_obs function to the database that Martin uses to visualise:
```sql
CREATE OR REPLACE FUNCTION public.taxon_filter(taxon_id_param integer)
RETURNS TABLE (
    id integer,
    tile_id integer,
    taxon_id integer,
    obs_date timestamp,
    obs_count integer
) AS $$
BEGIN
    RETURN QUERY 
    SELECT
        tile_obs_count.id,
        tile_obs_count.tile_id,
        tile_obs_count.taxon_id,
        tile_obs_count.obs_date,
        tile_obs_count.obs_count
    FROM
        tile_obs_count
    WHERE
        tile_obs_count.taxon_id = taxon_id_param;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION public.square_grid_obs(z integer, x integer, y integer, query_params json)
RETURNS bytea
AS $$
DECLARE
  mvt bytea;
BEGIN
  SELECT INTO mvt ST_AsMVT(tile, 'square_grid_obs', 4096, 'geom') FROM (
    SELECT
        ST_AsMVTGeom(ST_Transform(square_grid.geom, 3857), ST_TileEnvelope(z, x, y), 4096, 64, true) AS geom,
        taxon_filter.obs_count  -- Include the obs_count column
    FROM
        square_grid
        INNER JOIN taxon_filter((query_params->>'taxon_id')::integer) ON square_grid.id = taxon_filter.tile_id  -- Join on id/tile_id
    WHERE ST_Intersects(square_grid.geom, ST_TileEnvelope(z, x, y))  -- Only include squares that intersect the tile bounds
    AND taxon_filter.obs_date >= (query_params->>'start_date')::date  -- Filter rows by start_date
    AND taxon_filter.obs_date <= (query_params->>'end_date')::date  -- Filter rows by end_date
  ) as tile WHERE geom IS NOT NULL;

  RETURN mvt;
END

$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;
```

6. Start the Martin tile server
```
cd martin
./martin
```

It should output a bunch of stuff, hopefully including `Discovered source square_grid_obs from function public.square_grid_obs(integer, integer, integer, json) -> bytea`. Let it run in its own terminal.

7. Open a new terminal and run `streamlit run streamlit-app.py`. If you want to test different combinations of visualisations, you can select a species from the list, copy the taxon_id and paste it in the `list_of_filters` list above the `grid_layer` url. Date doesn't do much with the test dataset as it only contains observations for a couple of days.