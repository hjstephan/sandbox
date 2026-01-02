#!/bin/bash

# Pfad zum Git-Ordner
GIT_DIR="$HOME/Git"

# Prüfen, ob der Ordner existiert
if [ ! -d "$GIT_DIR" ]; then
    echo "Error: Folder $GIT_DIR does not exist."
    exit 1
fi

# Durch alle Unterordner iterieren
for repo in "$GIT_DIR"/*; do
    # Prüfen, ob es ein Verzeichnis ist
    if [ -d "$repo" ]; then
        # Prüfen, ob es ein Git-Repository ist
        if [ -d "$repo/.git" ]; then
            echo "Repository: $(basename "$repo")"
            
            # In das Repository wechseln und git pull ausführen
            cd "$repo" || continue
            git pull origin main
            
            echo ""
        else
            echo "Skip $repo (no Git repository)"
        fi
    fi
done

echo "Done."
