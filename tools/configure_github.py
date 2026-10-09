"""Apply repository presentation and protection through the user's GitHub CLI."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = 'Durel1/Personal_Manager'
ROOT = Path(__file__).resolve().parents[1]


def gh(*arguments, json_result=False):
    result = subprocess.run(['gh', *arguments], cwd=ROOT, check=True,
                            capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout) if json_result else result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protect-main', action='store_true')
    parser.add_argument('--delete-merged-branches', action='store_true')
    args = parser.parse_args()
    if not shutil.which('gh'):
        raise SystemExit('Installez GitHub CLI puis exécutez gh auth login.')
    gh('auth', 'status')
    gh('repo', 'edit', REPO, '--description',
       'Application Python de gestion locale : clients, équipes, rendez-vous, finances, rôles et exports Excel/PDF.',
       '--add-topic', 'python,customtkinter,sqlite,desktop-application,matplotlib,bcrypt',
       '--delete-branch-on-merge')
    print('Description, topics et suppression automatique après fusion configurés.')
    if args.protect_main:
        checks = gh('api', f'repos/{REPO}/commits/main/check-runs', json_result=True)['check_runs']
        if not any(c['name'] == 'test' and c['status'] == 'completed' and c['conclusion'] == 'success'
                   for c in checks):
            raise SystemExit('Attendez la réussite du contrôle test sur main avant la protection.')
        branch = gh('api', f'repos/{REPO}/branches/main', json_result=True)
        if branch['protected']:
            print('main est déjà protégée ; aucune règle existante n’a été remplacée.')
        else:
            rules = dict(required_status_checks=dict(strict=True, contexts=['test']),
                         enforce_admins=True, restrictions=None,
                         required_pull_request_reviews=dict(dismiss_stale_reviews=True,
                             require_code_owner_reviews=False, required_approving_review_count=0),
                         allow_force_pushes=False, allow_deletions=False)
            with tempfile.TemporaryDirectory() as directory:
                file = Path(directory)/'protection.json'
                file.write_text(json.dumps(rules), encoding='utf-8')
                gh('api', '--method', 'PUT', f'repos/{REPO}/branches/main/protection', '--input', str(file))
            print('main protégée : PR obligatoire, test réussi et branche à jour ; aucun approbateur imposé.')
    if args.delete_merged_branches:
        branches = gh('api', '--paginate', '--slurp', f'repos/{REPO}/branches?per_page=100', json_result=True)
        main_sha = gh('api', f'repos/{REPO}/branches/main', json_result=True)['commit']['sha']
        for branch in (branch for page in branches for branch in page):
            name, sha = branch['name'], branch['commit']['sha']
            if name == 'main' or branch['protected'] or not name.startswith(('refactor/phase-', 'feat/phase-', 'chore/phase-')):
                continue
            comparison = gh('api', f'repos/{REPO}/compare/{main_sha}...{sha}', json_result=True)
            if comparison['status'] not in ('behind', 'identical'):
                print(f'Conservée (commits non intégrés) : {name}')
                continue
            # Lease prevents deletion if someone pushed since the ancestry check.
            subprocess.run(['git', 'push', f'--force-with-lease=refs/heads/{name}:{sha}',
                            f'https://github.com/{REPO}.git', f':refs/heads/{name}'], cwd=ROOT, check=True)
            print(f'Branche intégrée supprimée : {name}')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(f'Commande refusée (code {error.returncode}). Vérifiez vos droits GitHub et réessayez.')
