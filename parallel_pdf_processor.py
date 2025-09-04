#!/usr/bin/env python3
"""
📚 PDF Learning System - Parallel Processor with Auto-Deployment
Processes all PDFs in parallel and automatically deploys to GitHub Pages
"""

import os
import json
import glob
import threading
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from enhanced_ai_processor import EnhancedAIPDFProcessor
from html_generator import HTMLGenerator
import subprocess
import shutil

class ParallelPDFLearningSystem:
    def __init__(self):
        self.processor = EnhancedAIPDFProcessor()
        self.html_generator = HTMLGenerator()
        self.pdfs_dir = "pdfs"
        self.output_dir = "."  # Changed to current directory
        self.index_file = "index.html"
        self.processed_pdfs = []
        self.lock = threading.Lock()
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.pdfs_dir, exist_ok=True)
        print(f"📁 Created directory: {self.pdfs_dir}")
    
    def get_pdf_files(self):
        """Get all PDF files from the pdfs directory"""
        pdf_pattern = os.path.join(self.pdfs_dir, "*.pdf")
        pdf_files = glob.glob(pdf_pattern)
        print(f"📄 Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def process_single_pdf(self, pdf_path):
        """Process a single PDF and generate HTML page"""
        try:
            pdf_name = os.path.basename(pdf_path)
            print(f"\n🚀 Starting processing: {pdf_name}")
            
            # Process PDF with AI
            content_data = self.processor.process_pdf_with_structured_content(pdf_path)
            
            # Generate HTML page
            output_filename = self.generate_html_page(pdf_path, content_data)
            
            # Store info for index page
            pdf_info = {
                'title': content_data['subject_info']['title'],
                'icon': content_data['subject_info']['icon'],
                'filename': output_filename,
                'stats': content_data['stats'],
                'original_pdf': pdf_name,
                'processed_at': datetime.now().strftime("%H:%M:%S")
            }
            
            # Thread-safe addition to processed list
            with self.lock:
                self.processed_pdfs.append(pdf_info)
                # Update index page after each completion
                self.update_index_page()
            
            print(f"✅ Completed: {pdf_name} -> {output_filename}")
            return pdf_info
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(pdf_path)}: {e}")
            return None
    
    def process_all_pdfs_parallel(self, max_workers=3):
        """Process all PDFs in parallel"""
        print("🚀 PDF Learning System - Parallel Processing")
        print("=" * 50)
        
        # Setup directories
        self.setup_directories()
        
        # Get all PDF files
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("❌ No PDF files found in the 'pdfs' directory")
            print(f"📁 Please place your PDF files in: {os.path.abspath(self.pdfs_dir)}")
            return
        
        # Create initial index page
        self.create_initial_index_page(len(pdf_files))
        
        # Process PDFs in parallel
        print(f"\n🔄 Processing {len(pdf_files)} PDFs in parallel (max {max_workers} workers)...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all PDFs for processing
            future_to_pdf = {executor.submit(self.process_single_pdf, pdf_path): pdf_path 
                           for pdf_path in pdf_files}
            
            # Process completed tasks
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    if result:
                        print(f"🎉 Successfully processed: {os.path.basename(pdf_path)}")
                    else:
                        print(f"❌ Failed to process: {os.path.basename(pdf_path)}")
                except Exception as e:
                    print(f"❌ Exception processing {os.path.basename(pdf_path)}: {e}")
        
        print(f"\n🎉 Parallel processing complete! Generated {len(self.processed_pdfs)} HTML pages")
        print(f"📄 Final index page: {self.index_file}")
        
        # Auto-deploy to GitHub Pages
        if self.processed_pdfs:
            self.deploy_to_github_pages()
    
    def generate_html_page(self, pdf_path, content_data):
        """Generate HTML page for a single PDF"""
        # Extract base name and split by hyphen to get folder name
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Split by hyphen and clean up
        parts = base_name.split(' - ', 1)  # Split on first occurrence of ' - '
        
        if len(parts) > 1:
            # Extract folder name (part before hyphen) and content name (part after hyphen)
            folder_name = parts[0].strip()
            content_name = parts[1].strip()
            
            # Create clean folder name
            clean_folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create clean content name for HTML file
            clean_content_name = "".join(c for c in content_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create folder path (now at same level as output_dir)
            folder_path = os.path.join(self.output_dir, clean_folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Generate HTML filename without the folder name
            output_filename = f"{clean_content_name}.html"
            output_path = os.path.join(folder_path, output_filename)
            
            # Return relative path from current directory for index page
            relative_filename = os.path.join(clean_folder_name, output_filename)
        else:
            # Fallback: no hyphen found, use original logic
            clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_filename = f"{clean_name}.html"
            output_path = os.path.join(self.output_dir, output_filename)
            relative_filename = output_filename
        
        # Generate HTML content
        html_content = self.html_generator.generate_html_content(content_data)
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return relative_filename
    
    def deploy_to_github_pages(self):
        """Automatically deploy to GitHub Pages"""
        print("\n🚀 Starting automatic deployment to GitHub Pages...")
        
        # Get GitHub token from environment or prompt user
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            print("🔑 GitHub Personal Access Token not found in environment.")
            print("💡 Please set GITHUB_TOKEN environment variable or enter it when prompted.")
            github_token = input("Enter your GitHub Personal Access Token: ").strip()
            if not github_token:
                print("❌ No token provided. Deployment cancelled.")
                return
        
        try:
            # Check if git is available
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            
            # Setup deployment
            deploy_dir = "deploy_temp"
            if os.path.exists(deploy_dir):
                shutil.rmtree(deploy_dir)
            os.makedirs(deploy_dir)
            
            # Copy files for deployment
            print("📁 Preparing files for deployment...")
            
            # Copy index file
            shutil.copy(self.index_file, os.path.join(deploy_dir, "index.html"))
            
            # Copy all generated HTML files and folders
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith('.html'):
                        # Get the relative path from current directory
                        rel_path = os.path.relpath(root, self.output_dir)
                        if rel_path == '.':
                            # File is directly in current directory
                            shutil.copy(os.path.join(root, file), os.path.join(deploy_dir, file))
                        else:
                            # File is in a subfolder
                            target_dir = os.path.join(deploy_dir, rel_path)
                            os.makedirs(target_dir, exist_ok=True)
                            shutil.copy(os.path.join(root, file), os.path.join(target_dir, file))
            
            # Copy README if exists
            if os.path.exists("README.md"):
                shutil.copy("README.md", os.path.join(deploy_dir, "README.md"))
            
            # Create .nojekyll file for GitHub Pages
            with open(os.path.join(deploy_dir, ".nojekyll"), "w") as f:
                f.write("")
            
            # Initialize git and push
            os.chdir(deploy_dir)
            
            # Initialize git repository
            subprocess.run(["git", "init"], check=True)
            
            # Set up remote with token
            remote_url = f"https://{github_token}@github.com/naveenpatil1/InteractiveLearning.git"
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
            
            # Add and commit files
            subprocess.run(["git", "add", "."], check=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-deploy: Update Interactive Learning System - {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push to main branch
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
            
            print("✅ Successfully deployed to GitHub Pages!")
            print("🌐 Your site is available at: https://naveenpatil1.github.io/InteractiveLearning/")
            print("⏱️  Changes will be live in 2-5 minutes")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            print("💡 Make sure your Personal Access Token has 'repo' permissions")
        except Exception as e:
            print(f"❌ Deployment error: {e}")
        finally:
            # Clean up
            os.chdir("..")
            if os.path.exists(deploy_dir):
                shutil.rmtree(deploy_dir)
    
    def create_initial_index_page(self, total_pdfs):
        """Create initial index page showing processing status"""
        initial_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>">
    <title>Disha's Learning System - Processing...</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 3em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .processing-status {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .spinner {{
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .progress {{
            background: #e2e8f0;
            border-radius: 10px;
            height: 20px;
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .progress-bar {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .pdf-list {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .pdf-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            background: #f8fafc;
            transition: all 0.3s ease;
        }}
        
        .pdf-item.processing {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
        }}
        
        .pdf-item.completed {{
            background: #dcfce7;
            border-left: 4px solid #16a34a;
        }}
        
        .pdf-item.failed {{
            background: #fee2e2;
            border-left: 4px solid #dc2626;
        }}
        
        .pdf-icon {{
            font-size: 1.5em;
            margin-right: 15px;
        }}
        
        .pdf-info {{
            flex: 1;
        }}
        
        .pdf-name {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .pdf-status {{
            font-size: 0.9em;
            color: #6b7280;
        }}
        
        .auto-refresh {{
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Disha's Learning System</h1>
            <p>Processing PDFs in Parallel - Real-time Updates</p>
        </div>
        
        <div class="processing-status">
            <div class="spinner"></div>
            <h2>🔄 Processing PDFs...</h2>
            <p>Processing {total_pdfs} PDF files in parallel</p>
            <div class="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <p id="progressText">0 / {total_pdfs} completed</p>
        </div>
        
        <div class="pdf-list">
            <h3>📄 PDF Processing Status</h3>
            <div id="pdfList">
                <!-- PDF items will be populated here -->
            </div>
        </div>
        
        <div class="auto-refresh">
            <p>🔄 This page auto-refreshes every 5 seconds</p>
            <p>⏰ Last updated: <span id="lastUpdate">{datetime.now().strftime("%H:%M:%S")}</span></p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setInterval(() => {{
            location.reload();
        }}, 5000);
        
        // Update progress bar
        function updateProgress(completed, total) {{
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const percentage = (completed / total) * 100;
            
            progressBar.style.width = percentage + '%';
            progressText.textContent = completed + ' / ' + total + ' completed';
        }}
    </script>
</body>
</html>"""
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        print(f"📄 Created initial index page: {self.index_file}")
    
    def update_index_page(self):
        """Update index page with current processed PDFs"""
        if not self.processed_pdfs:
            return
        
        # Generate cards for each processed PDF
        pdf_cards = ""
        for pdf_info in self.processed_pdfs:
            pdf_cards += f"""
            <div class="pdf-card" onclick="window.open('{pdf_info['filename']}', '_blank')">
                <div class="pdf-icon">{pdf_info['icon']}</div>
                <div class="pdf-info">
                    <h3>{pdf_info['title']}</h3>
                    <p class="pdf-stats">
                        📚 {pdf_info['stats']['total_concepts']} Concepts • 
                        📝 {pdf_info['stats']['total_mcqs']} MCQs • 
                        💭 {pdf_info['stats']['total_subjective']} Subjective Qs
                    </p>
                    <p class="pdf-original">Original: {pdf_info['original_pdf']}</p>
                    <p class="pdf-time">Processed at: {pdf_info['processed_at']}</p>
                </div>
                <div class="pdf-arrow">→</div>
            </div>
            """
        
        # Generate final index content
        index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disha's Learning System - Index</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 3em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            text-align: center;
            min-width: 150px;
        }}
        
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        
        .pdf-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .pdf-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .pdf-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        
        .pdf-icon {{
            font-size: 3em;
            min-width: 60px;
            text-align: center;
        }}
        
        .pdf-info {{
            flex: 1;
        }}
        
        .pdf-info h3 {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .pdf-stats {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .pdf-original {{
            color: #95a5a6;
            font-size: 0.8em;
            font-style: italic;
            margin-bottom: 3px;
        }}
        
        .pdf-time {{
            color: #10b981;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .pdf-arrow {{
            font-size: 1.5em;
            color: #667eea;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 0.9em;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Disha's Learning System</h1>
            <p>Content Generated Using Azure OpenAI GPT-4o</p>
            <div class="stats">
                <div class="stat">
                    <span class="number">{len(self.processed_pdfs)}</span>
                    <span class="label">PDF Documents</span>
                </div>
            </div>
        </div>
        
        <div class="pdf-grid">
            {pdf_cards}
        </div>
    </div>
    
    <div class="footer">
        <p>Disha's Learning System • {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        <p>🎓 Interactive Learning Content</p>
    </div>
</body>
</html>"""
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

# Usage
if __name__ == "__main__":
    system = ParallelPDFLearningSystem()
    system.process_all_pdfs_parallel(max_workers=3)  # Process 3 PDFs simultaneously
