## File & Text Search

* **Find files by name pattern recursively:**
```bash
  find . -name "*400-C*"
```

* **Search for text within files recursively:**
```bash
grep -r "Berlin" .

```

---

## PDF Tools

* **Create a searchable PDF (OCR):**
```bash
ocrmypdf input.pdf output_searchable.pdf

```


* **Extract text from PDF:**
```bash
pdftotext output_searchable.pdf output.txt

```


* **Convert HTML to PDF (A4 with margins):**
```bash
wkhtmltopdf --page-size A4 --margin-top 25mm \
--margin-bottom 25mm --margin-left 20mm \
--margin-right 20mm Lebenslauf.html Lebenslauf.pdf

```



---

## Development & Git

* **Pull and Rebase local changes:**
```bash
git pull --rebase origin main

```


* **Push changes after rebase:**
```bash
git push origin main

```


* **VS Code Extension - Build & Install:**
```bash
npm install && vsce package
code --install-extension java-refactoring-analyzer-0.0.1.vsix

```


* **NPM Testing:**
```bash
npm run test:unit      # Standard unit tests
npm run test:coverage  # With code coverage

```


* **Publish Extension:**
```bash
vsce publish -p $AZURE_TOKEN

```



---

## Database (PostgreSQL)

* **SchemaSpy Documentation:**
```bash
java -jar schemaspy-app.jar -t pgsql -host localhost:5432 \
-db hospital_db -s public -u hospital_admin -p dbpassword \
-dp ~/.m2/repository/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar \
-o doc/schemaspy -vizjs

```


* **Clean/Truncate Tables:**
```sql
TRUNCATE TABLE tracking_ids RESTART IDENTITY CASCADE;
TRUNCATE TABLE delivery_receipts RESTART IDENTITY CASCADE;

```


* **Database Export/Import:**
```bash
# Export
sudo -u postgres pg_dump consorsbank-parser > export.sql

# Drop, Recreate, and Import
sudo -u postgres psql -c 'DROP DATABASE "consorsbank-parser";'
sudo -u postgres psql -c 'CREATE DATABASE "consorsbank-parser" OWNER consorsuser;'
psql -U consorsuser -d consorsbank-parser -h localhost -p 5432 < export.sql

```



---

## Multimedia (yt-dlp)

* **Download Playlist as MP3 (Basic):**
```bash
yt-dlp -x --audio-format mp3 --output "%(artist)s-%(title)s.%(ext)s" [URL]

```


* **Advanced Download (High Quality & Metadata):**
```bash
yt-dlp \
--verbose \
--output "%(artist)s - %(title)s.%(ext)s" \
--yes-playlist \
--windows-filenames \
--abort-on-unavailable-fragment \
--buffer-size 1M \
--extract-audio \
--audio-format mp3 \
--audio-quality 320K \
--embed-metadata \
--download-archive _songs.txt \
"[https://www.youtube.com/playlist?list=PL0Vlic5oMPdtI9EW0p227GsJXkDuFRdTw](https://www.youtube.com/playlist?list=PL0Vlic5oMPdtI9EW0p227GsJXkDuFRdTw)"

```



---

## System & Cloud

* **Google Drive Sync (rclone):**
```bash
rclone sync googledrive: ~/GoogleDrive --progress
rclone sync googledrive: ~/GoogleDrive --dry-run

```


* **Install Legacy Ubuntu Wallpapers:**
```bash
sudo apt install ubuntu-wallpapers-{hirsute,groovy,focal,eoan,disco,cosmic,bionic,artful,zesty,yakkety,xenial,wily,vivid,utopic,trusty,saucy,raring,quantal,precise,oneiric,natty,maverick,lucid,karmic}

```



---

## Application Builds (Evolution Mail)

* **Compile from Source:**
```bash
rm -rf build && mkdir build && cd build/
cmake .. && make -j4
sudo make install && sudo ldconfig
sudo update-desktop-database /usr/local/share/applications

```


* **Sandbox Fixes (if needed):**
```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1
sudo chmod u+s /usr/bin/bwrap
export WEBKIT_FORCE_SANDBOX=0

```

---

## Application Builds (shotwell)

* **Initial Setup & Build:**
```bash
# Configure build with /usr/local prefix
meson setup builddir --prefix=/usr/local

# Build
ninja -C builddir

```

* **Test Build (without installing):**
```bash
 ./builddir/src/shotwell

```

* **Install to System:**
```bash
# Install to /usr/local
sudo ninja -C builddir install

```

* **Configure Library Path (one-time setup):**
```bash
# Find installed library location
find /usr/local -name "libshotwell-plugin-dev-1.0.so.0"

# Create ldconfig configuration
sudo nano /etc/ld.so.conf.d/local.conf
# Add line: /usr/local/lib/x86_64-linux-gnu

# Update library cache
sudo ldconfig

# Verify libraries are registered
ldconfig -p | grep shotwell

```

* **Rebuild & Reinstall After Changes:**
```bash
cd ~/Git/shotwell/
ninja -C builddir
sudo ninja -C builddir install

```


```

```
