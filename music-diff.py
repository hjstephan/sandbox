#!/usr/bin/env python3
"""
Vergleicht zwei Musikordner und zeigt die Unterschiede an.
Unterstützt normale Pfade und MTP/GVFS-Pfade (z.B. für Android-Geräte).
"""

import os
import sys
from pathlib import Path
from urllib.parse import unquote
import subprocess

def is_mtp_path(path):
    """Prüft ob es sich um einen MTP/GVFS-Pfad handelt."""
    return path.startswith('mtp://') or path.startswith('gvfs://') or path.startswith('afc://')

def convert_mtp_to_local(mtp_path):
    """
    Konvertiert MTP-Pfad zu lokalem GVFS-Mount-Pfad.
    GVFS mountet MTP-Geräte unter /run/user/UID/gvfs/
    """
    try:
        # Versuche den GVFS-Mount-Pfad zu finden
        uid = os.getuid()
        gvfs_root = f"/run/user/{uid}/gvfs"
        
        if not os.path.exists(gvfs_root):
            return None
            
        # Liste alle gemounteten GVFS-Pfade auf
        for mount in os.listdir(gvfs_root):
            mount_path = os.path.join(gvfs_root, mount)
            if 'mtp' in mount.lower():
                # Extrahiere den relativen Pfad aus der MTP-URL
                if '/Internal' in mtp_path or '/SD' in mtp_path:
                    parts = mtp_path.split('/')
                    # Finde den Index von 'Internal' oder ähnlichem
                    for i, part in enumerate(parts):
                        if 'Internal' in part or 'SD' in part or 'storage' in part:
                            rel_path = '/'.join(parts[i:])
                            rel_path = unquote(rel_path)
                            test_path = os.path.join(mount_path, rel_path)
                            if os.path.exists(test_path):
                                return test_path
                
                # Wenn nichts gefunden, gib den Mount-Pfad zurück
                return mount_path
        
        return None
    except Exception as e:
        print(f"Fehler bei MTP-Konvertierung: {e}")
        return None

def get_music_files(folder_path, extensions=None):
    """
    Sammelt alle Musikdateien aus einem Ordner (inkl. Unterordner).
    
    Args:
        folder_path: Pfad zum Ordner (kann auch MTP-Pfad sein)
        extensions: Liste der Dateiendungen (z.B. ['.mp3', '.flac'])
    
    Returns:
        Dictionary mit relativen Pfaden als Keys und absoluten Pfaden als Values
    """
    if extensions is None:
        extensions = ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma']
    
    # Prüfe ob es ein MTP-Pfad ist
    if is_mtp_path(folder_path):
        print(f"   MTP-Pfad erkannt, versuche zu konvertieren...")
        local_path = convert_mtp_to_local(folder_path)
        if local_path:
            print(f"   → Verwende lokalen Mount-Pfad: {local_path}")
            folder_path = local_path
        else:
            print(f"   ⚠️  Konnte MTP-Pfad nicht in lokalen Pfad umwandeln")
            print(f"   💡 Tipp: Stelle sicher, dass das Gerät verbunden und gemountet ist")
            print(f"   💡 Prüfe mit: ls /run/user/$(id -u)/gvfs/")
            return {}
    
    folder = Path(folder_path)
    music_files = {}
    
    if not folder.exists():
        print(f"⚠️  Ordner existiert nicht: {folder_path}")
        return music_files
    
    print(f"   Scanne: {folder}")
    
    try:
        for file in folder.rglob('*'):
            if file.is_file() and file.suffix.lower() in extensions:
                # Relativer Pfad zur besseren Vergleichbarkeit
                rel_path = file.relative_to(folder)
                music_files[str(rel_path)] = str(file)
    except PermissionError as e:
        print(f"⚠️  Berechtigungsfehler beim Scannen: {e}")
    except Exception as e:
        print(f"⚠️  Fehler beim Scannen: {e}")
    
    return music_files

def compare_folders(folder1, folder2):
    """
    Vergleicht zwei Musikordner und zeigt die Unterschiede.
    
    Args:
        folder1: Pfad zum ersten Ordner (z.B. Festplatte)
        folder2: Pfad zum zweiten Ordner (z.B. Smartphone via MTP)
    """
    print("🎵 Musikordner-Vergleich")
    print("=" * 60)
    print(f"Ordner 1: {folder1}")
    print(f"Ordner 2: {folder2}")
    print("=" * 60)
    print()
    
    # Dateien aus beiden Ordnern sammeln
    print("📂 Scanne Ordner...")
    files1 = get_music_files(folder1)
    print(f"   ✓ Ordner 1: {len(files1)} Dateien gefunden")
    
    files2 = get_music_files(folder2)
    print(f"   ✓ Ordner 2: {len(files2)} Dateien gefunden")
    print()
    
    # Unterschiede berechnen
    only_in_1 = set(files1.keys()) - set(files2.keys())
    only_in_2 = set(files2.keys()) - set(files1.keys())
    in_both = set(files1.keys()) & set(files2.keys())
    
    # Ergebnisse anzeigen
    print("📊 ERGEBNIS:")
    print("=" * 60)
    print()
    
    if only_in_1:
        print(f"💾 NUR in Ordner 1 ({len(only_in_1)} Dateien):")
        print(f"   → Diese von Ordner 1 nach Ordner 2 kopieren")
        print("-" * 60)
        for file in sorted(only_in_1)[:20]:  # Zeige nur erste 20
            print(f"   {file}")
        if len(only_in_1) > 20:
            print(f"   ... und {len(only_in_1) - 20} weitere")
        print()
    
    if only_in_2:
        print(f"📱 NUR in Ordner 2 ({len(only_in_2)} Dateien):")
        print(f"   → Diese von Ordner 2 nach Ordner 1 kopieren")
        print("-" * 60)
        for file in sorted(only_in_2)[:20]:  # Zeige nur erste 20
            print(f"   {file}")
        if len(only_in_2) > 20:
            print(f"   ... und {len(only_in_2) - 20} weitere")
        print()
    
    if in_both:
        print(f"✅ In beiden Ordnern ({len(in_both)} Dateien)")
        print()
    
    # Zusammenfassung
    print("=" * 60)
    print("📋 ZUSAMMENFASSUNG:")
    print(f"   Gesamt in Ordner 1: {len(files1)}")
    print(f"   Gesamt in Ordner 2: {len(files2)}")
    print(f"   In beiden:          {len(in_both)}")
    print(f"   Nur in Ordner 1:    {len(only_in_1)}")
    print(f"   Nur in Ordner 2:    {len(only_in_2)}")
    print("=" * 60)

if __name__ == "__main__":
    # Prüfe ob genau 2 Argumente übergeben wurden
    if len(sys.argv) != 3:
        print("Verwendung: python3 musik_vergleich.py <Ordner1> <Ordner2>")
        print()
        print("Beispiele:")
        print("  # Normale Ordner")
        print("  python3 musik_vergleich.py ~/Music /media/usb/Music")
        print()
        print("  # Mit MTP-Gerät (Android-Smartphone)")
        print("  python3 musik_vergleich.py ~/Music 'mtp://...'")
        print()
        print("💡 Tipp für MTP-Geräte:")
        print("   1. Öffne den Dateimanager (Nautilus/Dolphin)")
        print("   2. Klicke auf dein Smartphone")
        print("   3. Navigiere zum Musik-Ordner")
        print("   4. Verwende den realen Pfad unter /run/user/$(id -u)/gvfs/")
        print()
        print("   Oder finde ihn mit:")
        print("   ls -la /run/user/$(id -u)/gvfs/")
        sys.exit(1)
    
    ordner1 = sys.argv[1]
    ordner2 = sys.argv[2]
    
    # Vergleich durchführen
    compare_folders(ordner1, ordner2)
