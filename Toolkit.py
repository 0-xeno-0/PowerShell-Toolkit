#!/usr/bin/env python3

"""
SYNOPSIS
    Author: ABHISHEK KISHOR SINGH
    Created_Date: 25 October, 2025
    
    DESCRIPTION
        A menu-driven Python toolkit for automating common manual tasks on Windows.
        This is a conversion of the PowerShell 'Toolkit.ps1'.
    
    USAGE
        Run this script (python Toolkit.py) to access all 13 tools from one 
        convenient, menu-driven interface.
"""

import os
import sys
import shutil
import subprocess
import random
import string
import csv
import time
import getpass
import re
import socket
import ctypes
import importlib
import smtplib
from datetime import datetime, timedelta
from urllib.parse import urljoin
from email.message import EmailMessage

# --- Third-Party Imports ---
# These must be installed via pip:
# pip install colorama requests beautifulsoup4 psutil
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("Error: 'colorama' library not found. Please run: pip install colorama")
    # Create dummy color objects so the script doesn't crash
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = DummyColor()
    Style = DummyColor()

# =============================================================================
# SCRIPT CONFIGURATION (EDIT THESE)
# =============================================================================

# --- Config for Tool 9: TarBall Mailer ---
# This tool requires a valid SMTP server to send emails.
# Gmail/Google Workspace: smtp.gmail.com, port 587
# Outlook/Hotmail: smtp.office365.com, port 587
SMTP_SERVER = "smtp.your-email-provider.com"
SMTP_PORT = 587 
FROM_EMAIL = "your-script-email@gmail.com"

# =============================================================================
# UTILITY FUNCTIONS CENTER (The Toolkit)
# =============================================================================

def out_separator():
    """Prints a blue separator line."""
    print(Fore.BLUE + "--------------------------------------------------")

def out_header(title):
    """Prints a formatted cyan header."""
    out_separator()
    print(Fore.CYAN + title)
    out_separator()

def out_error(message):
    """Prints a red error message."""
    print(Fore.RED + f"[ERROR] {message}")

def out_success(message):
    """Prints a green success message."""
    print(Fore.GREEN + f"[SUCCESS] {message}")

def out_info(message):
    """Prints a yellow info message."""
    print(Fore.YELLOW + f"[INFO] {message}")

def check_pip_dependency(package_name):
    """Checks if a required Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        out_error(f"Python dependency missing: '{package_name}'")
        out_info(f"Please install it using: pip install {package_name}")
        return False

def is_admin():
    """Checks if the script is running with Administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def suspend_script(message="Press [Enter] to return to the main menu..."):
    """Pauses the script and waits for user input."""
    input(message)

def wait_script(seconds=2):
    """Pauses the script for a set number of seconds."""
    time.sleep(seconds)

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# =============================================================================
# FEATURE FUNCTIONS CENTER (The Tools)
# =============================================================================

# --- 1. Folder Organizer ---
def start_folder_organizer():
    out_header("Folder Organizer Utility")
    
    src_path = input("Enter the absolute path of the folder to organize: ")
    dest_path = input(r"Enter the destination path (default: ~\MyShebangs): ")
    
    # 2. Validate input
    if not dest_path:
        dest_path = os.path.join(os.path.expanduser('~'), "MyShebangs")
        out_info(f"Using default destination: {dest_path}")

    if not os.path.isdir(src_path):
        out_error(f"Source path '{src_path}' is not a valid directory. Aborting.")
        wait_script(2)
        return

    os.makedirs(dest_path, exist_ok=True)
    
    # Helper dictionary for file types
    EXT_MAP = {
        ".jpg": "images", ".jpeg": "images", ".png": "images",
        ".doc": "documents", ".docx": "documents", ".txt": "documents", ".pdf": "documents",
        ".xls": "spreadsheets", ".xlsx": "spreadsheets", ".csv": "spreadsheets",
        ".sh": "scripts", ".py": "scripts", ".ps1": "scripts",
        ".zip": "archives", ".tar": "archives", ".gz": "archives", ".bz2": "archives",
        ".ppt": "presentations", ".pptx": "presentations",
        ".mp3": "audio",
        ".mp4": "video",
    }
    
    special_files_log = os.path.join(dest_path, "specialFiles.list")
    files_moved = 0

    try:
        with open(special_files_log, 'w', encoding='utf-8') as log_file:
            log_file.write("--- Log of Uncategorized Files ---\n")
    except IOError as e:
        out_error(f"Could not write to log file: {e}")
        return

    out_info(f"Scanning '{src_path}'...")
    
    # 3. The Main Loop
    for filename in os.listdir(src_path):
        src_file = os.path.join(src_path, filename)
        
        if os.path.isfile(src_file):
            files_moved += 1
            ext = os.path.splitext(filename)[1].lower()
            
            subdir = EXT_MAP.get(ext)
            
            if subdir:
                target_dir = os.path.join(dest_path, subdir)
                os.makedirs(target_dir, exist_ok=True)
                
                try:
                    shutil.move(src_file, target_dir)
                    out_success(f"Moved {filename} -> {subdir}")
                except Exception as e:
                    out_error(f"Failed to move {filename}: {e}")
            else:
                # Log uncategorized files
                try:
                    with open(special_files_log, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"{filename}\n")
                    out_info(f"Logged '{filename}' to specialFiles.list")
                except IOError as e:
                    out_error(f"Failed to log {filename}: {e}")

    out_separator()
    if files_moved == 0:
        out_info(f"No files were found to move in '{src_path}'.")
    else:
        out_success(f"Organization complete. All files moved to '{dest_path}'.")
        out_info(f"Uncategorized files are logged in '{special_files_log}'")
    
    suspend_script()

# --- 2. Password Generator ---
def start_password_generator():
    out_header("Password Generator Utility")
    
    pass_len_input = input("Enter password length (default: 16): ")
    pass_len = 16

    try:
        if not pass_len_input:
            pass_len = 16
            out_info("Using default length: 16 characters.")
        else:
            pass_len = int(pass_len_input)
            if pass_len <= 0:
                out_error("Invalid input. Length must be a positive number.")
                wait_script(2)
                return
            if pass_len > 1024:
                out_error("Length too large. Please choose a length under 1024.")
                wait_script(2)
                return
    except ValueError:
        out_error("Invalid input. Length must be a positive number.")
        wait_script(2)
        return

    # 3. Generate Password
    char_set = string.ascii_letters + string.digits + '!@#$%^&*'
    
    out_info("Generating secure password...")
    password = "".join(random.choices(char_set, k=pass_len))
    
    # 4. Display Password
    out_separator()
    print("Your new password is:")
    print(Fore.YELLOW + password)
    out_separator()
    out_info("Copy this password to a safe place. It is not saved.")
    suspend_script()

# --- 3. Curf Remover (Safe File Cleaner) ---
def start_curf_remover():
    out_header("Curf Remover (Old File Cleaner)")
    
    out_info("This utility will find and delete files older than a specified number of days.")
    out_error("WARNING: This is a destructive operation. Files are permanently deleted.")
    out_info("We will *only* target FILES and EMPTY FOLDERS. Non-empty folders are safe.")
    out_separator()
    
    clean_path = input("Enter the absolute path of the folder to clean: ")
    days_input = input("Delete files OLDER than how many days? (default: 15): ")
    
    days = 15
    try:
        if not days_input:
            days = 15
        else:
            days = int(days_input)
            if days < 0:
                raise ValueError
    except ValueError:
        out_error("Invalid input. Days must be a non-negative number. Aborting.")
        wait_script(2)
        return
        
    if not os.path.isdir(clean_path):
        out_error(f"Path '{clean_path}' is not a valid directory. Aborting.")
        wait_script(2)
        return
    
    out_info(f"Searching for files in '{clean_path}' older than {days} days...")
    cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
    
    files_to_delete = []
    dirs_to_delete = []

    # Walk bottom-up to find empty dirs correctly
    for root, dirs, files in os.walk(clean_path, topdown=False):
        # 4. Find files
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.getmtime(file_path) < cutoff_time:
                    files_to_delete.append(file_path)
            except OSError:
                pass # Ignore files we can't access
        
        # Find *empty* directories
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path) and os.path.getmtime(dir_path) < cutoff_time:
                    dirs_to_delete.append(dir_path)
            except OSError:
                pass # Ignore dirs we can't access
    
    total_count = len(files_to_delete) + len(dirs_to_delete)
    if total_count == 0:
        out_success(f"No files or empty folders found older than {days} days.")
        wait_script(2)
        return
        
    out_separator()
    out_info(f"Found {len(files_to_delete)} files and {len(dirs_to_delete)} empty folders to delete.")
    print("You can review the list below:")
    
    for f in files_to_delete: print(f)
    for d in dirs_to_delete: print(d)
    
    out_separator()
    out_error("This action is permanent. Are you sure?")
    confirm = input("Type 'interactive' to confirm one-by-one, or 'ALL' to delete all: ")
    
    def delete_item(path, is_file=True):
        try:
            if is_file:
                os.remove(path)
                print(f"Deleted file: {path}")
            else:
                os.rmdir(path)
                print(f"Deleted empty dir: {path}")
        except OSError as e:
            out_error(f"Failed to delete {path}: {e}")

    if confirm == 'interactive':
        out_info("Starting interactive deletion...")
        for f in files_to_delete:
            if input(f"Delete file '{f}'? (y/n): ").lower() == 'y':
                delete_item(f, is_file=True)
        for d in dirs_to_delete:
            if input(f"Delete empty dir '{d}'? (y/n): ").lower() == 'y':
                delete_item(d, is_file=False)
        out_success("Interactive cleanup complete.")
    
    elif confirm == 'ALL':
        out_info("Starting bulk deletion...")
        for f in files_to_delete:
            delete_item(f, is_file=True)
        for d in dirs_to_delete:
            delete_item(d, is_file=False)
        out_success("Bulk cleanup complete.")
        
    else:
        out_info("Invalid confirmation. Aborting. No files were deleted.")
    
    suspend_script()

# --- 4. User Creator ---
def start_user_creator():
    out_header("User Creator Utility")
    
    if not is_admin():
        out_error("This action requires Administrator privileges.")
        out_info("Please run the script again as an Administrator.")
        wait_script(4)
        return
        
    out_info("Running with Administrator privileges. Ready to create user.")
    username = input("Enter the new username: ")
    
    if not username:
        out_error("Username cannot be empty. Aborting.")
        wait_script(2)
        return
        
    if ' ' in username:
        out_error("Invalid username. Spaces are not allowed.")
        wait_script(2)
        return

    # Check if user already exists using 'net user'
    check_proc = subprocess.run(['net', 'user', username], capture_output=True, text=True, shell=True)
    if check_proc.returncode == 0:
        out_error(f"User '{username}' already exists. Aborting.")
        wait_script(2)
        return
        
    out_info(f"You are about to create a new user named: {username}")
    confirm = input("Are you sure you want to proceed? (y/n): ").lower()
    
    if confirm != 'y':
        out_info("Aborting. No user was created.")
        wait_script(2)
        return
        
    try:
        out_info(f"Please enter the password for '{username}' now.")
        password = getpass.getpass("Enter new password: ")
        
        # Create the user
        add_proc = subprocess.run(
            ['net', 'user', username, password, '/add', '/comment:"User created by toolkit"'],
            capture_output=True, text=True, shell=True
        )
        
        if add_proc.returncode != 0:
            raise Exception(add_proc.stderr or add_proc.stdout)
            
        out_success(f"Successfully created user '{username}'.")
        out_info("Adding user to 'Users' group...")
        
        # Add to 'Users' group
        group_proc = subprocess.run(
            ['net', 'localgroup', 'Users', username, '/add'],
            capture_output=True, text=True, shell=True
        )
        
        if group_proc.returncode != 0:
            raise Exception(group_proc.stderr or group_proc.stdout)
            
        out_success(f"User '{username}' is ready.")
        
    except Exception as e:
        out_error(f"Failed to create user: {e}")
        wait_script(2)
        return
        
    suspend_script()

# --- 5. Indexer (Batch File Renamer) ---
def start_indexer():
    out_header("Indexer (Batch File Renamer)")
    
    target_dir = input("Enter the path to the directory with files to rename: ")
    prefix = input("Enter a new prefix for the files (e.g., 'report-'): ")
    
    if not os.path.isdir(target_dir):
        out_error(f"Directory '{target_dir}' does not exist. Aborting.")
        wait_script(2)
        return
        
    if not prefix:
        out_info("No prefix entered. Using 'file-' as default.")
        prefix = "file-"
        
    out_info(f"This will rename all files in '{target_dir}' to '{prefix}[number].[original_extension]'.")
    out_error("WARNING: This action is permanent.")
    confirm = input("Are you sure you want to proceed? (y/n): ").lower()
    
    if confirm != 'y':
        out_info("Aborting. No files were renamed.")
        wait_script(2)
        return

    i = 1
    renamed_count = 0
    
    try:
        for filename in os.listdir(target_dir):
            src_path = os.path.join(target_dir, filename)
            
            if os.path.isfile(src_path):
                # Get extension (e.g., ".jpg")
                base, extension = os.path.splitext(filename)
                
                # Build new name with 3-digit padding
                new_name = f"{prefix}{i:03d}{extension}"
                dest_path = os.path.join(target_dir, new_name)
                
                try:
                    os.rename(src_path, dest_path)
                    print(f"Renamed: {filename} -> {new_name}")
                    renamed_count += 1
                except OSError as e:
                    out_error(f"Failed to rename '{filename}': {e}")
                
                i += 1
    
    except Exception as e:
        out_error(f"An error occurred: {e}")

    out_separator()
    out_success(f"Renaming complete. {renamed_count} files were indexed.")
    suspend_script()

# --- 6. CSV Calculator ---
def start_csv_calculator():
    out_header("CSV Calculator")
    
    csv_file = input("Enter the path to your CSV file: ")
    has_header = input("Does this file have a header row? (y/n): ").lower()
    
    if not os.path.isfile(csv_file):
        out_error(f"File not found: '{csv_file}'. Aborting.")
        wait_script(2)
        return
        
    out_info(f"Parsing '{csv_file}'...")
    out_separator()
    line_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            if has_header == 'y':
                # Assumes headers 'Name', 'ID', 'Val1', 'Val2' as per original script
                out_info("Assuming headers are 'Name', 'ID', 'Val1', 'Val2'")
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        col1 = row['Name']
                        col2 = row['ID']
                        col3 = float(row['Val1'])
                        col4 = float(row['Val2'])
                        
                        total = col3 + col4
                        avg = total / 2
                        
                        print(f"Name: {col1}")
                        print(f"ID: {col2}")
                        print(Fore.GREEN + f"Total: {total}")
                        print(Fore.YELLOW + f"Average: {avg}")
                        print("")
                        line_count += 1
                        
                    except (KeyError, ValueError, TypeError):
                        out_info("Skipping malformed line...")
            
            else:
                # Assumes columns are [0], [1], [2], [3]
                reader = csv.reader(f)
                for row in reader:
                    try:
                        col1 = row[0]
                        col2 = row[1]
                        col3 = float(row[2])
                        col4 = float(row[3])
                        
                        total = col3 + col4
                        avg = total / 2
                        
                        print(f"Name: {col1}")
                        print(f"ID: {col2}")
                        print(Fore.GREEN + f"Total: {total}")
                        print(Fore.YELLOW + f"Average: {avg}")
                        print("")
                        line_count += 1
                        
                    except (IndexError, ValueError, TypeError):
                        out_info("Skipping malformed line...")

    except Exception as e:
        out_error(f"Failed to read file: {e}")
        
    out_separator()
    out_success(f"Calculation complete. Processed {line_count} valid lines.")
    suspend_script()

# --- 7. Service Manager ---
def start_service_manager():
    out_header("Service Manager")
    
    if not is_admin():
        out_error("This action requires Administrator privileges.")
        out_info("Please run the script again as an Administrator.")
        wait_script(4)
        return
        
    service_name = input("Enter the name of the service (e.g., 'WinRM', 'Spooler'): ")
    
    if not service_name:
        out_error("No service name entered. Aborting.")
        wait_script(2)
        return

    # Check status using 'sc query'
    try:
        proc = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True, check=True, shell=True)
        output = proc.stdout
        
        state_match = re.search(r"STATE\s+:\s+\d+\s+([A-Z_]+)", output)
        if not state_match:
            raise Exception("Could not parse service state.")
            
        status = state_match.group(1)
        out_separator()
        
        if status == "RUNNING":
            out_success(f"Service '{service_name}' is ACTIVE and RUNNING.")
            out_separator()
            action = input("Do you want to (s)top or (r)estart this service? (any other key to exit): ").lower()
            
            if action == 's':
                out_info(f"Attempting to STOP '{service_name}'...")
                subprocess.run(['net', 'stop', service_name], check=True, shell=True)
                out_success("Service stopped.")
            elif action == 'r':
                out_info(f"Attempting to RESTART '{service_name}'...")
                subprocess.run(['net', 'stop', service_name], check=True, shell=True)
                wait_script(1) # Give it a second
                subprocess.run(['net', 'start', service_name], check=True, shell=True)
                out_success("Service restarted.")
            else:
                out_info("No action taken.")
                
        elif status == "STOPPED":
            out_info(f"Service '{service_name}' is INACTIVE (stopped).")
            out_separator()
            action = input("Do you want to (s)tart this service? (y/n): ").lower()
            
            if action == 'y':
                out_info(f"Attempting to START '{service_name}'...")
                subprocess.run(['net', 'start', service_name], check=True, shell=True)
                out_success("Service started.")
            else:
                out_info("No action taken.")
                
        else:
            out_error(f"Service '{service_name}' is in a '{status}' state.")
            out_separator()
            out_info("Check Event Viewer (System log) for details.")
            action = input("Do you want to attempt a (r)estart? (y/n): ").lower()
            
            if action == 'y':
                out_info(f"Attempting to RESTART '{service_name}'...")
                subprocess.run(['net', 'stop', service_name], check=False, shell=True) # Allow failure
                wait_script(1)
                subprocess.run(['net', 'start', service_name], check=True, shell=True)
                out_success("Restart attempted.")
            else:
                out_info("No action taken.")
                
    except subprocess.CalledProcessError as e:
        if "1060" in e.stderr or "1060" in e.stdout:
            out_error(f"Could not find service '{service_name}'.")
        else:
            out_error(f"An error occurred: {e.stderr or e.stdout}")
        wait_script(2)
    
    suspend_script()

# --- 8. Online Image Extractor ---
def start_image_extractor():
    out_header("Online Image Extractor")
    
    # Dependency check
    if not (check_pip_dependency("requests") and check_pip_dependency("bs4")):
        suspend_script()
        return
        
    import requests
    from bs4 import BeautifulSoup
    
    target_url = input("Enter the full website URL to scan (e.g., https://example.com): ")
    save_dir = input(r"Enter directory to save images (default: ~\Downloads\ExtractedImages): ")
    
    if not target_url:
        out_error("No URL provided. Aborting.")
        wait_script(2)
        return
        
    if not save_dir:
        save_dir = os.path.join(os.path.expanduser('~'), "Downloads", "ExtractedImages")
        
    try:
        os.makedirs(save_dir, exist_ok=True)
    except OSError as e:
        out_error(f"Could not create save directory: {save_dir}. {e}")
        out_info("Please check permissions. Aborting.")
        wait_script(3)
        return
        
    out_info(f"Save directory set: {save_dir}")
    out_info(f"Starting download from '{target_url}'...")
    out_info("This may take some time...")
    
    downloaded_count = 0
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        page = requests.get(target_url, headers=headers)
        page.raise_for_status() # Raise error for bad responses (4xx, 5xx)
        
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Find all links (<a> tags) matching image extensions, as per original script
        image_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and any(href.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                image_links.append(href)
        
        # Also find all <img> tags (a logical improvement)
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and any(src.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                image_links.append(src)
                
        # Remove duplicates
        image_links = list(set(image_links))
        
        for img_url in image_links:
            # Handle relative URLs
            full_url = urljoin(target_url, img_url)
            
            try:
                # Get just the filename
                file_name = os.path.basename(full_url.split('?')[0]) # Split on '?' to remove query params
                if not file_name:
                    file_name = f"image_{downloaded_count}.jpg" # Fallback
                
                out_path = os.path.join(save_dir, file_name)
                
                out_info(f"Downloading {file_name} from {full_url}...")
                img_data = requests.get(full_url, headers=headers)
                img_data.raise_for_status()
                
                with open(out_path, 'wb') as f:
                    f.write(img_data.content)
                downloaded_count += 1
                
            except Exception as e:
                out_error(f"Failed to download {full_url}: {e}")

    except requests.exceptions.RequestException as e:
        out_error(f"Failed to download page or images: {e}")
    
    out_separator()
    if downloaded_count > 0:
        out_success(f"Download complete. Saved {downloaded_count} images to '{save_dir}'.")
    else:
        out_info("Scan complete. No images matching (jpg, jpeg, png, gif) were found.")
        try:
            os.rmdir(save_dir) # Clean up empty dir
        except OSError:
            pass
            
    suspend_script()

# --- 9. TarBall Mailer (Backup & Notify) ---
def start_tarball_mailer():
    out_header("TarBall Mailer (Backup & Notify)")
    
    out_info("This tool uses 'shutil.make_archive' (to .zip) and 'smtplib' (for email).")
    out_info(f"Email will be sent via: {SMTP_SERVER} from {FROM_EMAIL}")
    out_error("You must edit the SCRIPT CONFIGURATION at the top of this .py file.")
    
    src_dir = input("Enter the full path of the SOURCE directory to backup: ")
    dest_dir = input("Enter the full path of the DESTINATION directory for the backup: ")
    email_addr = input("Enter the email address for notification: ")

    if not os.path.isdir(src_dir):
        out_error(f"Source directory '{src_dir}' does not exist. Aborting.")
        wait_script(2)
        return
        
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email_addr):
        out_error("Invalid email address format. Aborting.")
        wait_script(2)
        return
        
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        out_error(f"Could not create destination directory '{dest_dir}': {e}")
        wait_script(3)
        return
        
    # Prepare for archive
    src_folder_name = os.path.basename(os.path.normpath(src_dir))
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"{src_folder_name}_{date_str}" # shutil adds .zip
    full_backup_path_base = os.path.join(dest_dir, backup_filename)
    
    out_info(f"Preparing to archive '{src_dir}'...")
    out_info(f"Target file: {full_backup_path_base}.zip")
    
    try:
        # 5. Execution (Create Archive)
        archive_path = shutil.make_archive(
            base_name=full_backup_path_base,
            format='zip',
            root_dir=src_dir
        )
        
        out_success("Backup archive created successfully!")
        out_separator()
        out_info(f"Sending email notification to {email_addr}...")
        
        # 6. Send Email
        subject = f"[Backup SUCCESS] {src_folder_name}"
        body = f"""Backup of '{src_dir}' was successfully created.
        
File: {archive_path}
Host: {socket.gethostname()}
Date: {datetime.now()}"""

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email_addr
        
        # Get password (modern SMTP requires auth)
        out_info(f"Please enter the password for {FROM_EMAIL} to send the email:")
        email_pass = getpass.getpass()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(FROM_EMAIL, email_pass)
            s.send_message(msg)
            
        out_success("Email notification sent.")
        
    except Exception as e:
        out_error(f"Operation FAILED: {e}")
        out_info("No email notification will be sent.")
        # Clean up partial archive
        if os.path.exists(f"{full_backup_path_base}.zip"):
            os.remove(f"{full_backup_path_base}.zip")
        wait_script(2)
        return
        
    suspend_script()

# --- 10. Term/Phase Fetcher ---
def start_term_fetcher():
    out_header("Term/Phase Fetcher (grep)")
    
    search_term = input("Enter the word or phrase to search for: ")
    search_dir = input("Enter directory to search in (default: current directory): ")
    case_insensitive = input("Make search case-insensitive? (y/n): ").lower()
    
    if not search_term:
        out_error("No search term provided. Aborting.")
        wait_script(2)
        return
        
    if not search_dir:
        search_dir = "."
        out_info("Using current directory for search.")
        
    if not os.path.isdir(search_dir):
        out_error(f"Directory '{search_dir}' does not exist. Aborting.")
        wait_script(2)
        return
        
    term_to_search = search_term
    if case_insensitive == 'y':
        out_info("Running case-insensitive search...")
        term_to_search = search_term.lower()
    else:
        out_info("Running case-sensitive search...")
        
    out_info(f"Searching for '{search_term}' in '{search_dir}'...")
    out_separator()
    
    matches_found = 0
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        line_to_search = line
                        if case_insensitive == 'y':
                            line_to_search = line.lower()
                            
                        if term_to_search in line_to_search:
                            matches_found += 1
                            print(f"{Fore.CYAN}--- Match Found ---")
                            print(f"{Fore.GREEN}Path: {file_path}")
                            print(f"{Fore.YELLOW}Line {i+1}:{Fore.RESET} {line.strip()}")
                            print("")
                            
            except Exception as e:
                out_error(f"Could not read {file_path}: {e}")
                
    out_separator()
    if matches_found > 0:
        out_success(f"Search complete. Found {matches_found} matches.")
    else:
        out_Info(f"Search complete. No matches found for '{search_term}'.")
        
    suspend_script()

# --- 11. Network Diagnostic Tool ---
def start_network_diagnostics():
    out_header("Network Diagnostic Tool")
    
    domain = input("Enter a domain to test (default: google.com): ")
    if not domain:
        domain = "google.com"
        
    out_info("Running 3-step network diagnostic...")
    out_separator()
    
    all_passed = True
    
    # --- Step 1: Test Gateway (Local Network) ---
    gateway_ip = None
    try:
        # Use 'route print' to find the default gateway
        proc = subprocess.run(['route', 'print', '0.0.0.0'], capture_output=True, text=True, shell=True)
        # Find the first 0.0.0.0 route
        match = re.search(r'0\.0\.0\.0\s+0\.0\.0\.0\s+([\d\.]+)\s+', proc.stdout)
        if match:
            gateway_ip = match.group(1)
        
        if not gateway_ip:
            out_error("Could not determine gateway IP. Skipping Step 1.")
            all_passed = False
        else:
            out_info(f"Step 1/3: Pinging gateway ({gateway_ip})...")
            # -n 3 = send 3 packets
            ping_proc = subprocess.run(['ping', '-n', '3', gateway_ip], capture_output=True, shell=True)
            if ping_proc.returncode == 0:
                out_success("  [PASS] Gateway is reachable.")
            else:
                out_error("  [FAIL] Gateway is NOT reachable.")
                all_passed = False
                
    except Exception as e:
        out_error(f"Gateway test failed: {e}")
        all_passed = False

    # --- Step 2: Test Internet (External IP) ---
    out_Info("Step 2/3: Pinging public DNS (8.8.8.8)...")
    try:
        ping_proc = subprocess.run(['ping', '-n', '3', '8.8.8.8'], capture_output=True, shell=True)
        if ping_proc.returncode == 0:
            out_success("  [PASS] Public internet is reachable.")
        else:
            out_error("  [FAIL] Public internet is NOT reachable.")
            all_passed = False
    except Exception:
        out_error("  [FAIL] Public internet is NOT reachable.")
        all_passed = False
        
    # --- Step 3: Test DNS (Name Resolution) ---
    out_info(f"Step 3/3: Resolving domain ({domain})...")
    try:
        name, aliases, ip_list = socket.gethostbyname_ex(domain)
        out_success("  [PASS] DNS resolution is working.")
        print(f"  {name} -> {ip_list}")
    except socket.gaierror:
        out_error("  [FAIL] DNS resolution FAILED.")
        all_passed = False
        
    # --- Final Report ---
    out_separator()
    if all_passed:
        out_success("All network checks passed. Connectivity is good! 🚀")
    else:
        out_error("One or more network checks failed. Please review.")
        
    suspend_script()

# --- 12. System Health Dashboard ---
def start_system_health():
    out_header("System Health Dashboard")
    
    if not check_pip_dependency("psutil"):
        suspend_script()
        return
        
    import psutil
    
    host_name = socket.gethostname()
    
    clear_screen()
    out_header(f"System Health Report for: {host_name}")
    
    # --- Uptime & Load ---
    print(Fore.CYAN + "--- Uptime & Load ---")
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        print(f"Uptime: {uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes")
        
        cpu_load = psutil.cpu_percent(interval=1)
        print(f"CPU Load: {cpu_load}%")
    except Exception as e:
        out_error(f"Could not get CPU/Uptime info: {e}")
    print("")

    # --- Memory Usage ---
    print(Fore.CYAN + "--- Memory Usage ---")
    try:
        mem = psutil.virtual_memory()
        def to_gb(bytes_val):
            return round(bytes_val / (1024**3), 2)
            
        print(f"Total: {to_gb(mem.total)} GB")
        print(f"Used:  {to_gb(mem.used)} GB")
        print(f"Free:  {to_gb(mem.available)} GB ({mem.percent}% used)")
    except Exception as e:
        out_error(f"Could not get Memory info: {e}")
    print("")
    
    # --- Filesystem Disk Usage ---
    print(Fore.CYAN + "--- Filesystem Disk Usage ---")
    print(f"{'Drive':<6} {'Label':<20} {'Type':<8} {'Size (GB)':>10} {'Free (GB)':>10} {'% Free':>8}")
    print("-" * 64)
    try:
        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or not part.fstype:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = to_gb(usage.total)
                free_gb = to_gb(usage.free)
                percent_free = round((usage.free / usage.total) * 100, 2)
                
                # Get drive label
                label = ""
                try:
                    # This is a bit of a hack to get volume label on Windows
                    label_proc = subprocess.run(['vol', part.mountpoint], capture_output=True, text=True, shell=True)
                    label_match = re.search(r"Volume in drive [A-Z] is (.*)", label_proc.stdout)
                    if label_match:
                        label = label_match.group(1).strip()
                except Exception:
                    pass
                    
                print(f"{part.mountpoint:<6} {label:<20} {part.fstype:<8} {total_gb:>10} {free_gb:>10} {percent_free:>8}")
            except Exception:
                continue # Skip inaccessible drives (e.g., card readers)
    except Exception as e:
        out_error(f"Could not get Disk info: {e}")
    print("")
    
    out_separator()
    suspend_script()

# --- 13. Log File Analyzer ---
def start_log_analyzer():
    out_header("Log File Analyzer (Windows Events)")
    
    log_name = input("Enter Log Name (e.g., Application, System, Security): ")
    log_level = input("Enter Log Level (e.g., Error, Warning, Information): ").lower()
    line_count = input("How many recent lines to show? (default: 10): ")
    
    # Map friendly names to event log level numbers
    level_map = {
        "error": 2,
        "warning": 3,
        "information": 4,
        "critical": 1, # Add critical
    }
    
    level_num = level_map.get(log_level)
    if level_num is None:
        out_error(f"Invalid Log Level: '{log_level}'. Must be Error, Warning, or Information.")
        wait_script(2)
        return
        
    try:
        count = int(line_count) if line_count else 10
    except ValueError:
        out_error("Invalid input. Lines must be a number.")
        wait_script(2)
        return

    out_info(f"Searching '{log_name}' log for the {count} most recent '{log_level}' events...")
    out_separator()
    
    try:
        # Use wevtutil, the command-line equivalent of Get-WinEvent
        xpath_query = f"*[System[Level={level_num}]]"
        
        cmd = [
            'wevtutil', 'qe', f'/l:{log_name}',
            f'/c:{count}', '/rd:true', # /rd:true = reverse (most recent first)
            f'/q:{xpath_query}', '/f:Text' # /f:Text = formatted text
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if proc.returncode != 0:
            if "No events were found" in proc.stderr:
                out_info("Search complete. No matches found.")
            else:
                raise Exception(proc.stderr or proc.stdout)
        else:
            print(proc.stdout)
            out_separator()
            out_success("Search complete. Showing most recent matches.")
            
    except Exception as e:
        out_error(f"An error occurred: {e}")
        out_info("Please ensure the Log Name is correct (e.g., 'System').")

    suspend_script()


# =============================================================================
# MAIN MENU & SCRIPT LOGIC CENTER (The Engine)
# =============================================================================

def show_main_menu():
    """Displays the main menu text."""
    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + "[##] ... XENO'S TOOLKIT ... [##]" + Style.RESET_ALL)
    print(Fore.CYAN + "Select an option to proceed:")
    print("")
    print(" 1. Folder Organizer")
    print(" 2. Password Generator")
    print(" 3. Curf Remover (Safe File Cleaner)")
    print(" 4. User Creation")
    print(" 5. Indexer (Batch File Renamer)")
    print(" 6. CSV Calculator")
    print(" 7. Service Manager")
    print(" 8. Online Image Extractor")
    print(" 9. TarBall Mailer (.ZIP)")
    print("10. Term/Phase Fetcher")
    print("11. Network Diagnostic Tool")
    print("12. System Health Dashboard")
    print("13. Log File Analyzer")
    print("")
    print(Fore.RED + " q. Quit")
    out_separator()

# Map menu choices to their respective functions
MENU_OPTIONS = {
    '1': start_folder_organizer,
    '2': start_password_generator,
    '3': start_curf_remover,
    '4': start_user_creator,
    '5': start_indexer,
    '6': start_csv_calculator,
    '7s': start_service_manager,
    '8': start_image_extractor,
    '9': start_tarball_mailer,
    '10': start_term_fetcher,
    '11': start_network_diagnostics,
    '12': start_system_health,
    '13': start_log_analyzer,
}

def main():
    """Main execution loop for the toolkit."""
    while True:
        show_main_menu()
        choice = input("Enter your choice: ")
        
        if choice.lower() == 'q':
            print("Ending Process!")
            break
            
        # Get the function from the dictionary
        action = MENU_OPTIONS.get(choice)
        
        if action:
            try:
                action() # Execute the chosen function
            except Exception as e:
                out_error(f"An unexpected error occurred in {action.__name__}: {e}")
                suspend_script()
        else:
            out_error(f"Invalid option '{choice}'. Please try again.")
            wait_script(2)

if __name__ == "__main__":
    main()
