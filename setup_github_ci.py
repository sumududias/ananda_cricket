#!/usr/bin/env python
"""
Setup script for GitHub CI/CD integration with PythonAnywhere.
This script helps push changes to GitHub and provides instructions for setting up secrets.
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

def check_git_status():
    """Check if git is initialized and has a remote"""
    # Check if .git directory exists
    if not os.path.exists(".git"):
        print("Git repository not initialized. Initializing...")
        run_command("git init")
    
    # Check if remote exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        print("No remote repository found.")
        repo_url = input("Enter your GitHub repository URL: ")
        run_command(f"git remote add origin {repo_url}")

def commit_and_push_changes():
    """Commit and push changes to GitHub"""
    # Add all files
    run_command("git add .")
    
    # Commit changes
    commit_message = input("Enter commit message (default: 'Update CI/CD configuration'): ")
    if not commit_message:
        commit_message = "Update CI/CD configuration"
    run_command(f'git commit -m "{commit_message}"')
    
    # Push to GitHub
    branch_name = "main"
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    current_branch = result.stdout.strip()
    if current_branch:
        branch_name = current_branch
    
    print(f"Pushing to {branch_name} branch...")
    run_command(f"git push -u origin {branch_name}")

def print_secrets_instructions():
    """Print instructions for setting up GitHub secrets"""
    print("\n" + "="*80)
    print("GITHUB SECRETS SETUP INSTRUCTIONS")
    print("="*80)
    print("\nTo enable automated deployment to PythonAnywhere, you need to set up the following secrets in your GitHub repository:")
    print("\n1. Go to your GitHub repository")
    print("2. Click on 'Settings' tab")
    print("3. Click on 'Secrets and variables' in the left sidebar, then 'Actions'")
    print("4. Click on 'New repository secret' and add the following secrets:")
    print("\n   PYTHONANYWHERE_HOST: ssh.pythonanywhere.com")
    print("   PYTHONANYWHERE_USERNAME: anandacricket")
    print("   PYTHONANYWHERE_PASSWORD: your_pythonanywhere_password")
    print("\nNOTE: Replace 'your_pythonanywhere_password' with your actual PythonAnywhere password.")
    print("\nAfter setting up these secrets, your CI/CD pipeline will automatically:")
    print("1. Run tests when you push to GitHub")
    print("2. Deploy to PythonAnywhere when tests pass on the main branch")
    print("="*80)

def main():
    """Main function"""
    print("Setting up GitHub CI/CD integration for Ananda Cricket")
    
    # Check git status
    check_git_status()
    
    # Ask to commit and push changes
    should_push = input("Do you want to commit and push changes to GitHub now? (y/n): ").lower()
    if should_push == 'y':
        commit_and_push_changes()
    
    # Print instructions for setting up secrets
    print_secrets_instructions()

if __name__ == "__main__":
    main()
