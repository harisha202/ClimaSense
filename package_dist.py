"""
ClimaSense Distribution Packaging Script
Creates a clean, production-ready distribution archive of ClimaSense.

Enforces strict exclusion rules:
- Excludes sensitive credentials (.env, api.env)
- Excludes Git repository (.git/)
- Excludes private runtime data and caches (instance/app.db, __pycache__, .pytest_cache)
- Excludes any existing archives (*.zip) preventing nested archives
- Preserves local developer database, .git repository, and dev environment intact
"""

import os
import sys
import shutil
import zipfile
import tempfile

# Excluded directory names (exact match)
EXCLUDE_DIRS = {
    '.git',
    '.pytest_cache',
    '__pycache__',
    'instance',
    'dist_staging',
    'scratch',
    '.vscode',
    '.idea',
    'htmlcov',
    'venv',
    '.venv',
    'env'
}

# Excluded file patterns and names
EXCLUDE_FILES = {
    'api.env',
    '.env',
    '.coverage',
    'ClimaSense_clean.zip'
}

def is_excluded(rel_path):
    parts = rel_path.replace('\\', '/').split('/')
    
    # Check directory components
    for part in parts[:-1]:
        if part in EXCLUDE_DIRS:
            return True
            
    filename = parts[-1]
    
    # Check exact filename exclusions
    if filename in EXCLUDE_FILES:
        return True
        
    # Check file extensions to exclude
    if filename.endswith(('.pyc', '.pyo', '.pyd', '.zip', '.tar', '.gz', '.db', '.sqlite3', '.log')):
        return True
        
    # Exclude any .env file other than .env.example
    if filename.endswith('.env') and filename != '.env.example':
        return True
        
    return False

def build_distribution(output_zip='ClimaSense_clean.zip'):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    output_path = os.path.abspath(os.path.join(root_dir, output_zip))
    
    print(f"[*] Building clean ClimaSense distribution archive: {output_zip}")
    print(f"[*] Source directory: {root_dir}")
    
    # Create a temporary file for writing the zip archive to avoid partial/in-place race
    temp_dir = tempfile.mkdtemp(prefix='climasense_dist_')
    temp_zip_path = os.path.join(temp_dir, 'temp_dist.zip')
    
    file_count = 0
    total_uncompressed_bytes = 0
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(root_dir):
                # Prune excluded directories in-place so os.walk does not recurse into them
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for f in sorted(files):
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, root_dir)
                    
                    if is_excluded(rel_path):
                        continue
                        
                    zf.write(abs_path, rel_path)
                    file_count += 1
                    total_uncompressed_bytes += os.path.getsize(abs_path)
                    
        # Verification audit on the generated archive
        print(f"[*] Packaged {file_count} files ({total_uncompressed_bytes / (1024*1024):.2f} MB uncompressed)")
        print("[*] Auditing archive contents...")
        
        audit_violations = []
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            for item in zf.namelist():
                if is_excluded(item):
                    audit_violations.append(item)
                    
        if audit_violations:
            raise RuntimeError(f"Audit failed! Prohibited files found in archive: {audit_violations}")
            
        # Safely copy to final destination
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(temp_zip_path, output_path)
        
        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"[+] SUCCESS: Distribution archive created cleanly: {output_path} ({final_size_mb:.2f} MB)")
        return output_path
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    build_distribution()
