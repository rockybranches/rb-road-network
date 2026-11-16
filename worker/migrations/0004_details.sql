-- Fully detailed results (see src/rbnet/detail.py).
--
-- The detailed GeoJSON is megabytes, too large for a D1 row, so it is kept
-- in the R2 bucket bound as DETAILS under details/{id}.geojson. These
-- columns track the background job that builds it:
--   detail_status   NULL (never asked for), 'queued', 'running', 'done', 'failed'
--   detail_points   reached cells in the file, once done
--   detail_bytes    size of the file, once done

ALTER TABLE analyses ADD COLUMN detail_status TEXT
  CHECK (detail_status IN ('queued', 'running', 'done', 'failed'));
ALTER TABLE analyses ADD COLUMN detail_error TEXT;
ALTER TABLE analyses ADD COLUMN detail_requested_at TEXT;
ALTER TABLE analyses ADD COLUMN detail_completed_at TEXT;
ALTER TABLE analyses ADD COLUMN detail_points INTEGER;
ALTER TABLE analyses ADD COLUMN detail_bytes INTEGER;
