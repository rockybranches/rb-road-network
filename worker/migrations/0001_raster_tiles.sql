-- Raster tiles on the national analysis grid (see worker/src/rbnet/grid.py).
-- One row per 128x128-cell tile; `data` is the zlib-compressed cell bytes.
-- Keyed for the only query the engine makes: a rectangle of tiles in one
-- dataset and layer.
CREATE TABLE raster_tiles (
  dataset TEXT NOT NULL,
  layer   TEXT NOT NULL,
  ty      INTEGER NOT NULL,
  tx      INTEGER NOT NULL,
  data    BLOB NOT NULL,
  PRIMARY KEY (dataset, layer, ty, tx)
) WITHOUT ROWID;
