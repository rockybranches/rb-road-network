-- County attributes. `geoid` is state FIPS * 1000 + county FIPS, the same
-- number stored in each cell of the "counties" raster layer.
CREATE TABLE counties (
  geoid      INTEGER PRIMARY KEY,
  countyns   INTEGER NOT NULL,
  name       TEXT NOT NULL,
  namelsad   TEXT NOT NULL,
  state_fips TEXT NOT NULL,
  stusps     TEXT NOT NULL,
  intpt_lat  REAL NOT NULL,
  intpt_lon  REAL NOT NULL
);

-- Population by county and year (census counts and projections). No foreign
-- key to `counties`: the two tables are reloaded independently by the ingest
-- tools, and each reload replaces the whole table.
CREATE TABLE county_population (
  geoid      INTEGER NOT NULL,
  year       INTEGER NOT NULL,
  population INTEGER NOT NULL,
  source     TEXT NOT NULL,
  PRIMARY KEY (geoid, year)
) WITHOUT ROWID;
