# Sandbox

A collection of utility scripts and command reference documentation for various development, system administration, and data analysis tasks.

## Contents

### 📚 Command Reference

- **`cmds.md`** - Comprehensive command reference covering:
  - File and text search operations
  - PDF tools (OCR, text extraction, HTML to PDF conversion)
  - Git workflows and VS Code extension development
  - PostgreSQL database operations and SchemaSpy documentation
  - yt-dlp for multimedia downloads
  - System utilities (rclone for Google Drive sync, Ubuntu wallpapers)
  - Building applications from source (Evolution Mail, Shotwell)

### 🔧 Git Utilities

- **`git-pull.sh`** - Automated script to pull updates from all Git repositories in `~/Git`
  - Iterates through all subdirectories
  - Executes `git pull origin main` for each repository
  - Skips non-Git directories

- **`git-releases.sh`** - Lists tags and releases for all Git repositories
  - Shows the 10 most recent tags per repository
  - Displays associated GitHub releases using `gh` CLI
  - Useful for tracking version history across projects

### 🎵 Music Management

- **`music-diff.py`** - Compare music collections between two locations
  - Supports both local folders and MTP devices (Android smartphones)
  - Automatically converts MTP paths to local GVFS mount points
  - Shows files unique to each location and common files
  - Useful for syncing music between computer and mobile devices
  
- **`music-diff.txt`** - Example output showing synchronized music collection (1591 files)

### 📍 Location Data Analysis

- **`timeline-parser.py`** - Google Timeline Semantic Segments Parser
  - Parses Google Takeout timeline data in the new semantic segments format
  - Extracts activities (movement), visits (stays), GPS positions, and WiFi scans
  - Calculates distances using haversine formula
  - Provides detailed timeline analysis with activity breakdowns
  - Exports data to CSV format for further analysis
  - Handles various coordinate formats and data structures

## Usage Examples

### Git Management Scripts

#### git-pull.sh
Automatically updates all Git repositories in your `~/Git` directory.

```bash
# Make executable (first time only)
chmod +x git-pull.sh

# Run the script
./git-pull.sh
```

**Output:**
```
Repository: my-project
Already up to date.

Repository: another-repo
Updating abc123..def456
Fast-forward
 file.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

Done.
```

**Requirements:** All repositories must use `main` as the default branch.

---

#### git-releases.sh
Lists recent tags and GitHub releases for all repositories.

```bash
# Make executable (first time only)
chmod +x git-releases.sh

# Run the script
./git-releases.sh
```

**Output:**
```
=========================================
Repository: my-project
=========================================
Tags and Releases:
  v2.1.0         -> Release: Version 2.1.0 - Bug fixes
  v2.0.0         -> Release: Version 2.0.0 - Major update
  v1.5.3         -> (tag only, no release)
```

**Requirements:** GitHub CLI (`gh`) must be installed and authenticated.

---

### Music Management

#### music-diff.py
Compare music libraries between two locations (local folders or Android devices via MTP).

**Basic Usage:**
```bash
# Compare two local folders
python3 music-diff.py ~/Music /media/usb/Music

# Compare local folder with Android device (automatic MTP detection)
python3 music-diff.py ~/Music 'mtp://Google_Pixel_9a_DEVICEID/Internal%20shared%20storage/Music/'

# Using direct GVFS mount path
python3 music-diff.py ~/Music /run/user/$(id -u)/gvfs/mtp:host=YOUR_DEVICE/Internal\ shared\ storage/Music/
```

**Finding MTP Path:**
```bash
# List available MTP devices
ls -la /run/user/$(id -u)/gvfs/

# Example output:
# mtp:host=Google_Pixel_9a_4A181JEBF17841
```

**Output:**
```
🎵 Musikordner-Vergleich
============================================================
Ordner 1: Music/
Ordner 2: mtp://...
============================================================

📂 Scanne Ordner...
   ✓ Ordner 1: 1591 Dateien gefunden
   ✓ Ordner 2: 1591 Dateien gefunden

📊 ERGEBNIS:
============================================================

💾 NUR in Ordner 1 (45 Dateien):
   → Diese von Ordner 1 nach Ordner 2 kopieren
------------------------------------------------------------
   Artist - Song1.mp3
   Artist - Song2.mp3
   ...

📱 NUR in Ordner 2 (12 Dateien):
   → Diese von Ordner 2 nach Ordner 1 kopieren
------------------------------------------------------------
   Band - Track1.mp3
   ...

✅ In beiden Ordnern (1534 Dateien)

============================================================
📋 ZUSAMMENFASSUNG:
   Gesamt in Ordner 1: 1591
   Gesamt in Ordner 2: 1591
   In beiden:          1534
   Nur in Ordner 1:    45
   Nur in Ordner 2:    12
============================================================
```

**Supported Audio Formats:** MP3, FLAC, WAV, M4A, AAC, OGG, WMA

---

### Location Data Analysis

#### timeline-parser.py
Parse and analyze Google Timeline data exported from Google Takeout.

**Basic Usage:**
```bash
# Parse timeline file
python3 timeline-parser.py path/to/2024_JANUARY.json

# Parse and export to CSV
python3 timeline-parser.py path/to/2024_JANUARY.json --export-csv
```

**Getting Timeline Data:**
1. Go to [Google Takeout](https://takeout.google.com)
2. Select "Location History (Timeline)"
3. Choose "JSON" format
4. Download and extract the archive
5. Find files like `Semantic Location History/2024/2024_JANUARY.json`

**Output:**
```
Google Timeline Semantic Segments Parser
==================================================
Loaded 1250 semantic segments

Parsed 1250 total records:
  activity: 450
  visit: 380
  position: 320
  activity_record: 80
  wifi_scan: 20

=== TIMELINE ANALYSIS ===
Total records: 1250
Period: 2024-01-01 08:30 to 2024-01-31 22:45 (742.3 hours)

=== ACTIVITY BREAKDOWN ===
IN_PASSENGER_VEHICLE: 450 records (36.0%) - 15432.5m (15.43km)
STILL: 380 records (30.4%) - 0.0m (0.00km)
WALKING: 120 records (9.6%) - 2341.2m (2.34km)
GPS_POSITION: 320 records (25.6%)

=== TOTAL DISTANCE ===
Overall: 17773.7 meters (17.77 km)

Distance by activity type:
  IN_PASSENGER_VEHICLE: 15432.5m (15.43km) - 86.8% of total
  WALKING: 2341.2m (2.34km) - 13.2% of total

=== LOCATION DATA ===
Records with location data: 950/1250 (76.0%)

Data exported to timeline_semantic.csv
```

**CSV Export Fields:**
- `timestamp`, `end_timestamp` - Start and end times
- `date`, `time` - Formatted date and time
- `record_type` - Type of record (activity, visit, position, etc.)
- `activity_type` - Activity classification (WALKING, IN_VEHICLE, STILL, etc.)
- `probability` - Confidence level (0-1)
- `start_latitude`, `start_longitude` - Starting coordinates
- `end_latitude`, `end_longitude` - Ending coordinates
- `distance_meters` - Distance traveled
- `duration_seconds` - Duration of activity
- `place_id` - Google Place ID (for visits)
- `semantic_type` - Semantic location type (HOME, WORK, etc.)

## Requirements

### System Tools
- Git and GitHub CLI (`gh`)
- Python 3.x
- rclone (for Google Drive sync)
- PostgreSQL and related tools
- yt-dlp (for multimedia downloads)
- ocrmypdf, pdftotext, wkhtmltopdf (for PDF operations)

### Python Dependencies
The Python scripts use standard library modules, no additional packages required.

## Quick Reference Commands

See `cmds.md` for the complete command reference, including:
- Finding files: `find . -name "*pattern*"`
- Text search: `grep -r "text" .`
- Database operations: `pg_dump`, table truncation
- High-quality audio downloads with metadata
- Application building and installation

## Notes

- Git scripts assume repositories are located in `~/Git/`
- Music diff script automatically handles GVFS/MTP paths for Android devices
- Timeline parser supports the new Google Takeout semantic segments format
- All scripts include error handling and informative output

## License

These are personal utility scripts. Use and modify as needed.
