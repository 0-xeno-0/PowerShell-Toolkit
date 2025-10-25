# PowerShell-Toolkit: A Multi-Tool Utility Script

This is an interactive, menu-driven PowerShell script that consolidates 13+ common IT support and system administration tasks into a single, user-friendly utility.
This powershell script is also available in the form of a stand alone python script for windows execution.
This project was built with a focus on professional development practices, including robust error handling, input validation, dependency checking, and a clean, color-coded user interface.

---

### 🛠️ Features

This toolkit includes:
1.  **Folder Organizer:** Safely sorts files in a directory into subfolders by type (images, docs, etc.).
2.  **Password Generator:** Creates a secure, randomized password of a specified length.
3.  **Curf Remover (Safe File Cleaner):** Finds and safely deletes files/empty folders older than a specified number of days, with a "dry run" and interactive confirmation.
4.  **User Creator:** A privileged utility to safely add new users to the system.
5.  **Indexer (Batch File Renamer):** Safely renames all files in a directory with a specified prefix, *while preserving file extensions*.
6.  **CSV Calculator:** Parses a simple CSV file to perform calculations.
7.  **Service Manager (systemd):** A privileged utility to check the status of a system services and offer to start/stop/restart it.
8.  **Online Image Extractor:** Downloads all images (jpg, png, etc.) from a given URL.
9.  **TarBall Mailer:** Backs up a directory into a archive and sends an email notification.
10. **Term/Phase Fetcher:** A user-friendly wrapper for to find text in files recursively.
11. **Network Diagnostic Tool:** A 3-step troubleshooter that checks the gateway, internet, and DNS.
12. **System Health Dashboard:** A read-only screen showing system load, memory, and disk space.
13. **Log File Analyzer:** Finds the *most recent* error/warning lines from a specified log file.

---

### 🚀 How to Use in PowerShell

1.  **Clone the repository (or download the script):**
    ```PowerShell
    git clone [https://github.com/0-xeno-0/PowerShell-Toolkit.git](https://github.com/0-xeno-0/PowerShell-Toolkit.git)
    cd PowerShell-Toolkit
    ```
2.  **Make the script executable (one time only):**
    ```PowerShell
    Unblock-File -Path .\toolkit.ps1
    ```
3.  **Run the script:**
    ```PowerShell
    .\toolkit.ps1
    ```

### 🚀 How to Use in Python IDE for CMD or PowerShell

1.  **Clone the repository (or download the script):**
    ```PowerShell
    git clone [https://github.com/0-xeno-0/PowerShell-Toolkit.git](https://github.com/0-xeno-0/PowerShell-Toolkit.git)
    cd PowerShell-Toolkit
    ```
2.  **Make the script executable (one time only):**
    ```PowerShell
    Unblock-File -Path .\toolkit.py
    ```
3.  **Run the script:**
    ```PowerShell
    python3 toolkit.py
    ```
    
    *Note: Some features (like "User Creator" and "Service Manager") require privileges to run. Launch the script with privileged access to use them.*

### ⚠️ Note on Execution Policy
If you still get an error in step 3 about scripts being disabled, your system's Execution Policy is likely set to Restricted.

1. **To check your policy:**

```PowerShell
Get-ExecutionPolicy
```
2. **To allow scripts for your current session only (a safe option): Run this command, then try step 3 again.**

```PowerShell
Set-ExecutionPolicy RemoteSigned -Scope Process
```
3. **Important: Before running, you may need to install the required third-party libraries:**

```PowerShell
pip install colorama requests beautifulsoup4 psutil
```
