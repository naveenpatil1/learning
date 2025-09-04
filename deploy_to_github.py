#!/usr/bin/env python3
"""
🚀 GitHub Pages Deployment Script
Automatically pushes processed PDF pages to GitHub Pages
"""

import os
import subprocess
import shutil
import glob
from datetime import datetime

class GitHubPagesDeployer:
    def __init__(self):
        self.repo_url = "https://github.com/naveenpatil1/InteractiveLearning.git"
        self.branch = "main"
        self.deploy_dir = "deploy"
        
    def setup_deployment(self):
        """Setup deployment directory and git repository"""
        print("🚀 Setting up GitHub Pages deployment...")
        
        # Create deployment directory
        if os.path.exists(self.deploy_dir):
            shutil.rmtree(self.deploy_dir)
        os.makedirs(self.deploy_dir)
        
        # Initialize git repository
        os.chdir(self.deploy_dir)
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", self.repo_url], check=True)
        
        print("✅ Deployment directory setup complete")
        
    def copy_files_for_deployment(self):
        """Copy only the files needed for GitHub Pages"""
        print("📁 Copying files for deployment...")
        
        # Copy main index file
        shutil.copy("../index.html", "index.html")
        
        # Copy all generated HTML files
        output_files = glob.glob("../output/*.html")
        for file in output_files:
            filename = os.path.basename(file)
            shutil.copy(file, filename)
        
        # Copy README
        if os.path.exists("../README.md"):
            shutil.copy("../README.md", "README.md")
        
        # Create .nojekyll file for GitHub Pages
        with open(".nojekyll", "w") as f:
            f.write("")
            
        print(f"✅ Copied {len(output_files) + 2} files for deployment")
        
    def commit_and_push(self):
        """Commit and push changes to GitHub"""
        print("📤 Committing and pushing to GitHub...")
        
        try:
            # Add all files
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Update Interactive Learning System - {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push to main branch
            subprocess.run(["git", "push", "-u", "origin", self.branch], check=True)
            
            print("✅ Successfully pushed to GitHub!")
            print(f"🌐 Your site will be available at: https://naveenpatil1.github.io/InteractiveLearning/")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing to GitHub: {e}")
            print("💡 Make sure you have proper GitHub authentication set up")
            
    def deploy(self):
        """Main deployment function"""
        try:
            self.setup_deployment()
            self.copy_files_for_deployment()
            self.commit_and_push()
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
        finally:
            # Clean up
            if os.path.exists(self.deploy_dir):
                shutil.rmtree(self.deploy_dir)

def main():
    """Main function to run deployment"""
    deployer = GitHubPagesDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()
