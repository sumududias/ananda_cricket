#!/usr/bin/env python
"""
Script to clean large files from Git history and push to GitHub.
This is necessary because GitHub has a file size limit of 100MB.
"""
import os
import subprocess
import sys

def run_command(command, exit_on_error=True):
    """Run a shell command and print output"""
    print(f"\n>>> Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"WARNING: Command exited with code {result.returncode}")
        if exit_on_error:
            sys.exit(1)
    return result.returncode == 0

def main():
    """Main function to clean Git history"""
    print("Starting Git history cleanup...")
    
    # 1. Make sure we have the latest .gitignore
    print("\n=== Checking .gitignore ===")
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    # Make sure backup files are ignored
    if 'backups/' not in gitignore_content:
        print("Adding backups/ to .gitignore")
        with open('.gitignore', 'a') as f:
            f.write("\n# Backups\nbackups/\n*.sql\n*.zip\n")
    
    # 2. Create a new orphan branch
    print("\n=== Creating new clean branch ===")
    run_command("git checkout --orphan clean-branch")
    
    # 3. Add all files except those in .gitignore
    print("\n=== Adding files to new branch ===")
    run_command("git add .")
    
    # 4. Commit the files
    print("\n=== Committing files to new branch ===")
    run_command('git commit -m "Initial commit with clean history"')
    
    # 5. Delete the old main branch and rename the new one
    print("\n=== Replacing main branch ===")
    run_command("git branch -D main")
    run_command("git branch -m main")
    
    # 6. Force push to GitHub
    print("\n=== Force pushing to GitHub ===")
    print("This will overwrite the remote repository with your clean local repository.")
    print("Proceeding with force push...")
    
    run_command("git push -f origin main")
    
    print("\n=== Git history cleanup completed successfully ===")
    print("Your repository should now be free of large files and ready to use with GitHub.")

if __name__ == "__main__":
    main()
