# Development notes

## Recommended Bugfixes

Based on the error trace and code analysis, here are the key bugfixes:

### 1. **Missing Error Handling for Failed Shapefile Opens** (Primary Issue)
   - **Location**: utils.hpp
   - **Problem**: `SHPOpen()` is called without checking if the file exists or opened successfully. When a shapefile doesn't exist, `SHPOpen()` returns `NULL`, but the code doesn't validate this before calling `SHPGetInfo()` on line 698 and 749.
   - **Impact**: Causes null pointer dereference when shapefile paths are invalid or missing
   - **Fix**: Add null checks after every `SHPOpen()` call:
   ```cpp
   shphand = SHPOpen(shapepath.c_str(), "rb");
   if (!shphand) {
       std::cerr << "Error: Unable to open " << shapepath << std::endl;
       continue;  // or throw exception
   }
   ```

### 2. **Empty Vector Access Causing Out-of-Range Exception** (Crash Source)
   - **Location**: utils.hpp
   - **Problem**: The assertion checks if `rpvec` is non-empty, but when the shapefile fails to load (due to bug #1), this assertion throws `std::out_of_range` with the message about vector size 0.
   - **Impact**: Cascading failure from bug #1
   - **Fix**: The assertion message is correct, but needs better context. Should report which shapefile(s) failed to load before the assertion.

### 3. **No Validation of Shapefile Directory Structure**
   - **Location**: utils.hpp
   - **Problem**: Code assumes `gis_extra_path` exists and contains valid shapefile geometry files, but doesn't validate this
   - **Fix**: Add directory existence check and error handling:
   ```cpp
   fs::path gis_extra_path = fs::path(rb::RB_DATA_PATH) / "gis_osm_roads_extra/";
   if (!fs::exists(gis_extra_path)) {
       throw std::runtime_error("Shapefile directory not found: " + gis_extra_path.string());
   }
   ```

### 4. **No Primary Shapefile Fallback Logic**
   - **Location**: utils.hpp
   - **Problem**: `shapefn` is initialized as global but may remain empty if no matching shapefile is found. No validation occurs before using it.
   - **Fix**: Add explicit check after the loop:
   ```cpp
   if (shapefn.empty()) {
       throw std::runtime_error("No primary roads shapefile found for the requested area");
   }
   ```

### 5. **Similar Issue in Places.hpp**
   - **Location**: places.hpp and [places.hpp#L280]
   - **Problem**: Same pattern - `SHPOpen()` without null check
   - **Fix**: Apply the same null-check pattern

### 6. **Missing Break Statement** (Minor)
   - **Location**: justPop.cc
   - **Problem**: Case 'f' lacks a `break;` statement, causing fall-through to case '?'
   - **Fix**: Add `break;` after line 180

### Summary
The immediate crash is caused by missing shapefile(s) due to unchecked `SHPOpen()` failures, leading to empty `rpvec` which triggers the assertion. The fixes should add proper error handling with informative messages so users know which data files are missing. 

Completed: *Document bugfixes for user* (1/1)