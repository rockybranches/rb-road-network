-- Stored analyses and the batches that group them.
--
-- A row is created 'pending' (batch upload) or 'done' (single analysis).
-- Running a pending row fills in the result columns, or records why it
-- failed. `result` is the full JSON the API returns; the few figures list
-- views and the batch summary need are also kept as plain columns.
-- `area` is the coarse reachable-area grid (see src/rbnet/area.py), tens of
-- kilobytes at most, well under D1's 2 MB row limit.

CREATE TABLE batches (
  id         TEXT PRIMARY KEY,
  label      TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE analyses (
  id                TEXT PRIMARY KEY,
  batch_id          TEXT,              -- NULL for a stand-alone analysis
  seq               INTEGER NOT NULL DEFAULT 0,  -- row order within a batch
  label             TEXT NOT NULL DEFAULT '',
  lat               REAL NOT NULL,
  lon               REAL NOT NULL,
  radius_m          REAL NOT NULL,
  tons_per_person   REAL NOT NULL,
  min_km2           REAL NOT NULL,
  status            TEXT NOT NULL CHECK (status IN ('pending', 'done', 'failed')),
  error             TEXT,
  created_at        TEXT NOT NULL,
  completed_at      TEXT,
  counties          INTEGER,
  reached_km2       REAL,
  population_base   INTEGER,
  population_target INTEGER,
  result            TEXT,
  area              BLOB
);

CREATE INDEX analyses_by_batch ON analyses (batch_id, seq);
CREATE INDEX analyses_by_created ON analyses (created_at);
