import subprocess
import os

def is_git_directory(path = '.'):
    return subprocess.call(['git', '-C', path, 'status'], stderr=subprocess.STDOUT, stdout = open(os.devnull, 'w')) == 0

def get_git_revision_short_hash() -> str:
    if is_git_directory():
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    else: return 'Not run locally.'

def get_git_revision_hash() -> str:
    if is_git_directory(): return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    else: return 'Not run locally.'


def get_git_diff_master() -> str:
    if is_git_directory(): return subprocess.check_output(['git', 'diff', 'origin/master', 'HEAD']).decode('ascii')
    else: return 'Not run locally.'

def get_git_diff() -> str:
    if is_git_directory():
        # Get the list of files not ignored
        files = subprocess.check_output(['git', 'ls-files']).decode('ascii').strip().split('\n')
        if files:
            # Filter to only existing files to avoid git diff errors on moved/deleted files
            existing_files = [f for f in files if os.path.exists(f)]
            if existing_files:
                # Pass these files to git diff
                try:
                    return subprocess.check_output(['git', 'diff', 'HEAD'] + existing_files).decode('utf-8')
                except UnicodeDecodeError:
                    # Fallback for binary files or encoding issues
                    return subprocess.check_output(['git', 'diff', 'HEAD'] + existing_files).decode('utf-8', errors='ignore')
            else:
                return 'No tracked files exist to diff.'
        else:
            return 'No changes to show.'
    else:
        return 'Not run locally'
