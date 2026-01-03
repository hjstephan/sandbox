#!/usr/bin/env python3
"""
Git Commit Message Spell Checker
Corrects spelling in commit messages while preserving history.
WARNING: This rewrites git history - commit hashes will change!

Usage:
    python fix_commits.py ~/Git/
    python fix_commits.py ~/Git/my-repo
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

try:
    from spellchecker import SpellChecker
except ImportError:
    print("Installing required package: pyspellchecker...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyspellchecker"])
    from spellchecker import SpellChecker

try:
    import langdetect
except ImportError:
    print("Installing required package: langdetect...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langdetect"])
    import langdetect


def run_git_command(cmd: List[str], cwd: str, check=True) -> str:
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Error running command: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
        return ""


def is_git_repo(path: Path) -> bool:
    """Check if path is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            cwd=path,
            check=False
        )
        return result.returncode == 0
    except:
        return False


def find_git_repos(base_path: Path) -> List[Path]:
    """Find all git repositories in the given path."""
    repos = []
    
    # Check if base_path itself is a repo
    if is_git_repo(base_path):
        repos.append(base_path)
        return repos
    
    # Search for repos in subdirectories
    try:
        for item in base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if is_git_repo(item):
                    repos.append(item)
    except PermissionError:
        pass
    
    return repos


def check_clean_working_tree(repo_path: Path) -> bool:
    """Check if working tree is clean."""
    status = run_git_command(["git", "status", "--porcelain"], str(repo_path))
    return not status


def get_commit_list(repo_path: Path, branch: str = "HEAD") -> List[Tuple[str, str]]:
    """Get list of commits with hash and message."""
    output = run_git_command([
        "git", "log", "--format=%H|||%s", branch
    ], str(repo_path))
    
    if not output:
        return []
    
    commits = []
    for line in output.split('\n'):
        if line:
            hash_msg = line.split('|||', 1)
            if len(hash_msg) == 2:
                commits.append((hash_msg[0], hash_msg[1]))
    
    return list(reversed(commits))  # Oldest first


def detect_language(text: str) -> str:
    """Detect language of text (returns 'en' or 'de')."""
    try:
        lang = langdetect.detect(text)
        return 'de' if lang == 'de' else 'en'
    except:
        return 'en'  # Default to English


def spell_check_message(message: str, spell_en: SpellChecker, spell_de: SpellChecker) -> str:
    """Spell check a commit message and return corrected version."""
    import re
    
    # Detect language
    lang = detect_language(message)
    spell = spell_de if lang == 'de' else spell_en
    
    # Common phrase corrections (context-aware) - English
    phrase_corrections_en = {
        r'\bbachelor thesis\b': "bachelor's thesis",
        r'\bmaster thesis\b': "master's thesis",
        r'\bbachelor theses\b': "bachelor's theses",
        r'\bmaster theses\b': "master's theses",
        r'\bdoctor thesis\b': "doctoral thesis",
    }
    
    # Common phrase corrections (context-aware) - German
    phrase_corrections_de = {
        r'\bBachelor Thesis\b': "Bachelorarbeit",
        r'\bMaster Thesis\b': "Masterarbeit",
        r'\bbachelor thesis\b': "Bachelorarbeit",
        r'\bmaster thesis\b': "Masterarbeit",
    }
    
    phrase_corrections = phrase_corrections_de if lang == 'de' else phrase_corrections_en
    
    # Apply phrase corrections first
    corrected = message
    for pattern, replacement in phrase_corrections.items():
        match = re.search(pattern, corrected, flags=re.IGNORECASE)
        if match:
            matched_text = match.group()
            # For German, preserve original case; for English, use replacement case
            if lang == 'de' and matched_text[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            elif lang == 'en' and matched_text[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE, count=1)
    
    # For English: words that should NOT be capitalized in middle of sentence
    lowercase_words_en = {
        'insights', 'script', 'scripts', 'file', 'files', 'function', 'functions',
        'method', 'methods', 'class', 'classes', 'module', 'modules', 'package',
        'packages', 'library', 'libraries', 'framework', 'tool', 'tools', 'code',
        'documentation', 'readme', 'license', 'configuration', 'settings', 'options',
        'feature', 'features', 'bug', 'bugs', 'issue', 'issues', 'test', 'tests',
        'database', 'server', 'client', 'api', 'interface', 'component', 'components',
        'service', 'services', 'application', 'applications', 'system', 'systems',
        'version', 'release', 'update', 'updates', 'change', 'changes', 'fix', 'fixes',
        'refactor', 'refactoring', 'optimization', 'performance', 'security', 'style',
        'formatting', 'dependency', 'dependencies', 'build', 'deployment', 'testing',
        'implementation', 'design', 'architecture', 'structure', 'logic', 'algorithm',
        'data', 'model', 'models', 'view', 'views', 'controller', 'controllers',
        'repository', 'repositories', 'folder', 'folders', 'directory', 'directories',
        'thesis', 'theses', 'references', 'reference', 'education', 'subject'
    }
    
    # For German: All nouns should be capitalized!
    # Common German nouns that should be capitalized
    capitalized_nouns_de = {
        'datei', 'dateien', 'ordner', 'verzeichnis', 'verzeichnisse', 'funktion',
        'funktionen', 'methode', 'methoden', 'klasse', 'klassen', 'modul', 'module',
        'paket', 'pakete', 'bibliothek', 'bibliotheken', 'werkzeug', 'werkzeuge',
        'code', 'dokumentation', 'konfiguration', 'einstellungen', 'optionen',
        'feature', 'features', 'fehler', 'problem', 'probleme', 'test', 'tests',
        'datenbank', 'server', 'client', 'schnittstelle', 'komponente', 'komponenten',
        'dienst', 'dienste', 'anwendung', 'anwendungen', 'system', 'systeme',
        'version', 'release', 'aktualisierung', 'änderung', 'änderungen', 'bugfix',
        'refactoring', 'optimierung', 'performance', 'sicherheit', 'stil', 'formatierung',
        'abhängigkeit', 'abhängigkeiten', 'build', 'deployment', 'implementierung',
        'design', 'architektur', 'struktur', 'logik', 'algorithmus', 'daten',
        'modell', 'modelle', 'ansicht', 'ansichten', 'controller', 'repository',
        'repositories', 'verzeichnis', 'thesis', 'arbeit', 'abschlussarbeit',
        'bachelorarbeit', 'masterarbeit', 'referenzen', 'referenz', 'bildung',
        'ausbildung', 'studium', 'fach', 'fächer', 'einblick', 'einblicke',
        'skript', 'skripte', 'stärke', 'stärken', 'lebenslauf', 'readme',
        'insights', 'script'  # English words used in German commits
    }
    
    # Proper nouns and acronyms that should stay capitalized (both languages)
    always_capitalized = {
        'python', 'java', 'javascript', 'typescript', 'github', 'gitlab', 'docker',
        'kubernetes', 'react', 'vue', 'angular', 'node', 'sql', 'html', 'css',
        'json', 'xml', 'yaml', 'api', 'rest', 'graphql', 'aws', 'azure', 'gcp',
        'linux', 'windows', 'macos', 'android', 'ios', 'git', 'npm', 'yarn',
        'webpack', 'babel', 'eslint', 'prettier', 'jest', 'mocha', 'redux',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'kafka',
        'jenkins', 'travis', 'circleci', 'heroku', 'netlify', 'vercel',
        'gallup'  # Company name
    }
    
    # Now do word-by-word processing
    words = corrected.split()
    corrected_words = []
    
    for i, word in enumerate(words):
        # Keep words with special characters, URLs, etc.
        if any(c in word for c in ['/', ':', '@', '#', '_', '-']):
            corrected_words.append(word)
            continue
        
        # Keep all-caps words (likely acronyms)
        if word.isupper() and len(word) > 1:
            corrected_words.append(word)
            continue
        
        # Remove punctuation for processing
        clean_word = word.strip('.,!?;:"\'()[]{}')
        if not clean_word:
            corrected_words.append(word)
            continue
        
        # First word should be capitalized (both languages)
        if i == 0:
            if clean_word[0].islower():
                corrected_word = word.replace(clean_word, clean_word.capitalize())
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
            continue
        
        # Language-specific capitalization rules
        if lang == 'de':
            # German: Nouns should be capitalized
            word_lower = clean_word.lower()
            if word_lower in capitalized_nouns_de:
                # Capitalize the noun
                if clean_word[0].islower():
                    corrected_word = word.replace(clean_word, clean_word.capitalize())
                    corrected_words.append(corrected_word)
                else:
                    corrected_words.append(word)
                continue
        else:
            # English: Common words should be lowercase (unless proper nouns)
            if clean_word.lower() in lowercase_words_en and clean_word[0].isupper():
                if clean_word.lower() not in always_capitalized:
                    corrected_word = word.replace(clean_word, clean_word.lower())
                    corrected_words.append(corrected_word)
                else:
                    corrected_words.append(word)
                continue
        
        # Proper nouns should be capitalized correctly (both languages)
        if clean_word.lower() in always_capitalized:
            proper_case = clean_word.lower().capitalize()
            if clean_word != proper_case:
                corrected_word = word.replace(clean_word, proper_case)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
            continue
        
        # Check spelling
        if clean_word.lower() not in spell:
            correction = spell.correction(clean_word.lower())
            if correction and correction != clean_word.lower():
                # Preserve/apply proper capitalization
                if lang == 'de':
                    # In German, check if it's likely a noun (in spell checker as noun)
                    # For simplicity, keep original capitalization or capitalize if it looks like a noun
                    if i > 0 and correction[0].isupper():
                        correction = correction.capitalize()
                    elif clean_word[0].isupper():
                        correction = correction.capitalize()
                    else:
                        correction = correction.lower()
                else:
                    # English: lowercase unless first word
                    if clean_word[0].isupper() and i > 0:
                        correction = correction.lower()
                    elif clean_word[0].isupper():
                        correction = correction.capitalize()
                
                corrected_word = word.replace(clean_word, correction)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    
    return ' '.join(corrected_words)


def preview_changes(commits: List[Tuple[str, str]], spell_en: SpellChecker, spell_de: SpellChecker) -> List[Tuple[str, str, str]]:
    """Preview spelling corrections."""
    changes = []
    
    for commit_hash, message in commits:
        corrected = spell_check_message(message, spell_en, spell_de)
        if corrected != message:
            changes.append((commit_hash, message, corrected))
    
    return changes


def get_user_choice_for_commit(commit_hash: str, original: str, suggested: str, commit_num: int, total_commits: int) -> tuple:
    """
    Ask user what to do with a single commit.
    Returns: (action, new_message)
    action can be: 'accept', 'skip', 'edit', 'abort'
    """
    print(f"\n{'='*70}")
    print(f"Commit {commit_num}/{total_commits}")
    print(f"Hash: {commit_hash[:8]}")
    print('='*70)
    print(f"Original:  {original}")
    print(f"Suggested: {suggested}")
    print()
    print("Options:")
    print("  [y] Accept suggestion")
    print("  [s] Skip this commit (keep original)")
    print("  [e] Edit manually")
    print("  [a] Abort (stop processing)")
    print()
    
    while True:
        choice = input("Your choice [y/s/e/a]: ").strip().lower()
        
        if choice == 'y' or choice == 'yes':
            return ('accept', suggested)
        elif choice == 's' or choice == 'skip':
            return ('skip', original)
        elif choice == 'e' or choice == 'edit':
            print(f"\nCurrent message: {original}")
            new_message = input("Enter new commit message: ").strip()
            if new_message:
                print(f"New message: {new_message}")
                confirm = input("Confirm? [y/n]: ").strip().lower()
                if confirm == 'y' or confirm == 'yes':
                    return ('accept', new_message)
                else:
                    print("Edit cancelled, choose again.")
            else:
                print("Empty message not allowed, choose again.")
        elif choice == 'a' or choice == 'abort':
            return ('abort', original)
        else:
            print("Invalid choice. Please enter y, n, e, or a.")


def rewrite_commits_with_script(repo_path: Path, commit_changes: List[Tuple[str, str, str]]) -> bool:
    """Rewrite commits using git filter-branch with a shell script."""
    
    # Create the message filter as a shell script
    filter_script = "#!/bin/bash\n"
    filter_script += "MSG=\"$(cat)\"\n"
    filter_script += "case \"$MSG\" in\n"
    
    for _, old_msg, new_msg in commit_changes:
        # Escape special characters for shell
        old_escaped = old_msg.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        new_escaped = new_msg.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        filter_script += f'  "{old_escaped}")\n'
        filter_script += f'    echo "{new_escaped}"\n'
        filter_script += f'    ;;\n'
    
    filter_script += '  *)\n'
    filter_script += '    echo "$MSG"\n'
    filter_script += '    ;;\n'
    filter_script += 'esac\n'
    
    # Write the script to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
        f.write(filter_script)
        script_path = f.name
    
    try:
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Run git filter-branch
        result = subprocess.run(
            ["git", "filter-branch", "-f", "--msg-filter", script_path, "--", "--all"],
            cwd=str(repo_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error during filter-branch:")
            print(result.stderr)
            return False
        
        # Remove the refs/original/ namespace
        refs_result = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname)", "refs/original/"],
            cwd=str(repo_path),
            capture_output=True,
            text=True
        )
        refs_output = refs_result.stdout.strip()
        
        if refs_output:
            for ref in refs_output.split('\n'):
                if ref:
                    subprocess.run(
                        ["git", "update-ref", "-d", ref],
                        cwd=str(repo_path),
                        check=False
                    )
        
        # Clean up
        subprocess.run(
            ["git", "reflog", "expire", "--expire=now", "--all"],
            cwd=str(repo_path),
            check=False
        )
        subprocess.run(
            ["git", "gc", "--prune=now"],
            cwd=str(repo_path),
            check=False
        )
        
        return True
        
    finally:
        # Clean up the script file
        try:
            os.unlink(script_path)
        except:
            pass


def rewrite_history(repo_path: Path, changes: List[Tuple[str, str, str]]):
    """Rewrite git history with corrected commit messages."""
    if not changes:
        return False
    
    print(f"\nFound {len(changes)} commit(s) with potential corrections.")
    print("You will be asked for each commit whether to apply the correction.\n")
    
    # Ask user for each commit
    commit_changes = []  # List of (commit_hash, old_message, new_message)
    total = len(changes)
    
    for idx, (commit_hash, original, suggested) in enumerate(changes, 1):
        action, new_message = get_user_choice_for_commit(
            commit_hash, original, suggested, idx, total
        )
        
        if action == 'abort':
            print("\n⚠ Aborted by user.")
            return False
        elif action == 'accept':
            if new_message != original:
                commit_changes.append((commit_hash, original, new_message))
                print(f"✓ Will change to: {new_message}")
        elif action == 'skip':
            print(f"⊘ Keeping original: {original}")
    
    # If no changes were accepted, return
    if not commit_changes:
        print("\n⊘ No changes to apply.")
        return False
    
    print(f"\n{'='*70}")
    print(f"Summary: {len(commit_changes)} commit(s) will be changed:")
    print('='*70)
    for _, original, corrected in commit_changes:
        print(f"  • {original}")
        print(f"    → {corrected}")
        print()
    
    final_confirm = input("Apply these changes? [yes/no]: ").strip().lower()
    if final_confirm != 'yes':
        print("Aborted.\n")
        return False
    
    print("\nRewriting commit history...")
    
    success = rewrite_commits_with_script(repo_path, commit_changes)
    
    if success:
        print("✓ Commit history rewritten successfully!\n")
        return True
    else:
        print("✗ Failed to rewrite history.\n")
        return False


def process_repository(repo_path: Path, spell_en: SpellChecker, spell_de: SpellChecker) -> dict:
    """Process a single repository."""
    repo_name = repo_path.name
    
    print(f"\n{'='*70}")
    print(f"Repository: {repo_name}")
    print(f"Path: {repo_path}")
    print('='*70)
    
    # Check if working tree is clean
    if not check_clean_working_tree(repo_path):
        print("⚠ Working tree is not clean. Skipping this repository.")
        print("  Please commit or stash changes first.\n")
        return {"repo": repo_name, "status": "skipped", "reason": "dirty working tree"}
    
    # Get commits
    commits = get_commit_list(repo_path)
    if not commits:
        print("No commits found. Skipping.\n")
        return {"repo": repo_name, "status": "skipped", "reason": "no commits"}
    
    print(f"Found {len(commits)} commits to check.")
    
    # Preview changes
    changes = preview_changes(commits, spell_en, spell_de)
    
    if not changes:
        print("✓ No spelling errors found!\n")
        return {"repo": repo_name, "status": "clean", "changes": 0}
    
    # Rewrite history
    success = rewrite_history(repo_path, changes)
    
    if success:
        return {"repo": repo_name, "status": "corrected", "changes": len(changes)}
    else:
        return {"repo": repo_name, "status": "skipped", "reason": "user declined"}


def main():
    print("="*70)
    print("Git Commit Message Spell Checker - Multi-Repository Mode")
    print("="*70)
    print("\nWARNING: This will rewrite git history!")
    print("Make sure you have backups and understand the implications.\n")
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python fix_commits.py <path>")
        print("\nExamples:")
        print("  python fix_commits.py ~/Git/")
        print("  python fix_commits.py ~/Git/my-repo")
        sys.exit(1)
    
    base_path = Path(sys.argv[1]).expanduser().resolve()
    
    if not base_path.exists():
        print(f"Error: Path '{base_path}' does not exist!")
        sys.exit(1)
    
    # Find repositories
    print(f"Searching for git repositories in: {base_path}")
    repos = find_git_repos(base_path)
    
    if not repos:
        print("No git repositories found!")
        sys.exit(1)
    
    print(f"Found {len(repos)} repository/repositories:\n")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo.name}")
    print()
    
    # Initialize spell checker
    print("Initializing spell checkers (English & German)...")
    spell_en = SpellChecker(language='en')
    spell_de = SpellChecker(language='de')
    
    # Process each repository
    results = []
    for repo in repos:
        result = process_repository(repo, spell_en, spell_de)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    corrected = [r for r in results if r["status"] == "corrected"]
    clean = [r for r in results if r["status"] == "clean"]
    skipped = [r for r in results if r["status"] == "skipped"]
    
    if corrected:
        print(f"\n✓ Corrected ({len(corrected)}):")
        for r in corrected:
            print(f"  - {r['repo']}: {r['changes']} commit(s) fixed")
    
    if clean:
        print(f"\n✓ Clean ({len(clean)}):")
        for r in clean:
            print(f"  - {r['repo']}: No errors found")
    
    if skipped:
        print(f"\n⚠ Skipped ({len(skipped)}):")
        for r in skipped:
            reason = r.get('reason', 'unknown')
            print(f"  - {r['repo']}: {reason}")
    
    if corrected:
        print("\n" + "="*70)
        print("IMPORTANT: Commit hashes have changed in corrected repositories.")
        print("="*70)
        print("\nTo push the changes:")
        for r in corrected:
            repo = [rp for rp in repos if rp.name == r['repo']][0]
            print(f"\n  cd {repo}")
            print(f"  git status  # Verify changes")
            print(f"  git log --oneline -10  # Check commit messages")
            print(f"  git push --force origin main  # Or your branch name")
        print("\nNote: Use --force to overwrite remote history.")
        print("="*70)


if __name__ == "__main__":
    main()
