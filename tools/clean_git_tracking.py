"""Untrack generated/private files while preserving every local file."""
import subprocess
from pathlib import Path

def untrack_local_files(root):
    result = subprocess.check_output(['git','ls-files','-z'],cwd=root)
    names = result.decode('utf-8').split('\0')
    paths = [name for name in names if name and
             (name.startswith(('.idea/','.venv/')) or '/__pycache__/' in name
              or name.endswith(('.pyc','.pyo','.db','.sqlite','.sqlite3')))]
    if not paths:
        print('Aucun fichier local ou généré à retirer du suivi Git.')
        return []
    subprocess.run(['git','rm','--cached','-f','--ignore-unmatch','--',*paths],cwd=root,check=True,capture_output=True)
    return paths

def main():
    paths = untrack_local_files(Path(__file__).resolve().parents[1])
    if not paths:
        return
    print('Fichiers conservés sur le disque. Vérifiez git status puis créez le commit de nettoyage.')

if __name__ == '__main__':
    main()
