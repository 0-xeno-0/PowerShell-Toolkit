<#  SYNOPSIS
    Author: ABHISHEK KISHOR SINGH
    Created_Date: 24 October, 2025
    Last_Modified_Date: 
    
    DESCRIPTION
        A menu-driven PowerShell toolkit for automating common manual tasks.
    
    USAGE
        Run this script to access all 13 tools from one convenient, menu-driven
        interface, eliminating the need to execute separate commands.#>


# =============================================================================
# UTILITY FUNCTIONS CENTER (The Toolkit)
# =============================================================================

# --- Utility Functions (PowerShell uses Write-Host for color) ---
function Out-Separator {
    Write-Host "--------------------------------------------------" -ForegroundColor Blue
}

function Out-Header {
    param($Title)
    Out-Separator
    Write-Host $Title -ForegroundColor Cyan
    Out-Separator
}

function Out-Error {
    param($Message)
    # Write-Error is for terminating errors, Write-Host is for display
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Out-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Out-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

# --- Utility Function: Dependency Check ---
function Test-Dependency {
    param($CommandName)
    # 'Get-Command' checks if a command/alias/function exists
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) 
    {
        Out-Error "Dependency missing: '$CommandName' is not installed."
        Out-Info "Please install '$CommandName' to use this feature."
        return $false
    }
    return $true
}

function Suspend-Script {
    param($Message = "Press [Enter] to return to the main menu...")
    Read-Host -Prompt $Message | Out-Null
}

function Wait-Script {
    param($Seconds = 2)
    Start-Sleep -Seconds $Seconds
}

# =============================================================================
# FEATURE FUNCTIONS CENTER (The Tools)
# =============================================================================

# --- Feature Function: Folder Organizer ---
function Start-FolderOrganizer {
    Out-Header "Folder Organizer Utility"
    
    # 1. Get user input
    $srcPath = Read-Host "Enter the absolute path of the folder to organize"
    $destPath = Read-Host "Enter the destination path (default: ~\MyShebangs)"

    # 2. Validate input
    # Set default destination if input was empty
    if ([string]::IsNullOrEmpty($destPath)) {
        $destPath = "$env:USERPROFILE\MyShebangs"
        Out-Info "Using default destination: $destPath"
    }

    # Check if source directory exists
    if (-not (Test-Path $srcPath -PathType Container)) {
        Out-Error "Source path '$srcPath' is not a valid directory. Aborting."
        Wait-Script 2
        return
    }

    # Create destination directory (and its parents) if it doesn't exist
    # -Force acts like 'mkdir -p'
    New-Item -Path $destPath -ItemType Directory -Force | Out-Null
    
    # Helper function to move files
    function Move-FileHelper {
        param($FileItem, $SubDir)
        
        $targetDir = Join-Path $destPath $SubDir
        New-Item -Path $targetDir -ItemType Directory -Force | Out-Null 
        
        try {
            Move-Item -Path $FileItem.FullName -Destination $targetDir -ErrorAction Stop
            Out-Success "Moved $($FileItem.Name) -> $SubDir"
        }
        catch {
            Out-Error "Failed to move $($FileItem.Name)"
        }
    }
    
    $specialFilesLog = Join-Path $destPath "specialFiles.list"
    "--- Log of Uncategorized Files ---" | Set-Content -Path $specialFilesLog
    $filesMoved = 0

    # 3. The Main Loop
    Out-Info "Scanning '$srcPath'..."
    # Get-ChildItem -File is the PowerShell equivalent of 'find -type f'
    Get-ChildItem -Path $srcPath -File | ForEach-Object {
        $filesMoved++
        
        # PowerShell's 'switch' with -Wildcard is perfect for file extensions
        switch -Wildcard ($_.Extension) {
            { @(".jpg", ".jpeg", ".png") -contains $_ } { Move-FileHelper $_ "images" }
            { @(".doc", ".docx", ".txt", ".pdf") -contains $_ } { Move-FileHelper $_ "documents" }
            { @(".xls", ".xlsx", ".csv") -contains $_ } { Move-FileHelper $_ "spreadsheets" }
            ".sh" { Move-FileHelper $_ "scripts" }
            { @(".zip", ".tar", ".gz", ".bz2") -contains $_ } { Move-FileHelper $_ "archives" }
            { @(".ppt", ".pptx") -contains $_ } { Move-FileHelper $_ "presentations" }
            ".mp3" { Move-FileHelper $_ "audio" }
            ".mp4" { Move-FileHelper $_ "video" }
            default {
                $_.Name | Add-Content -Path $specialFilesLog
                Out-Info "Logged '$($_.Name)' to specialFiles.list"
            }
        }
    }

    Out-Separator
    if ($filesMoved -eq 0) {
        Out-Info "No files were found to move in '$srcPath'."
    }
    else {
        Out-Success "Organization complete. All files moved to '$destPath'."
        Out-Info "Uncategorized files are logged in '$specialFilesLog'"
    }
    
    Suspend-Script
}

# --- Feature Function: Password Generator ---
function Start-PasswordGenerator {
    Out-Header "Password Generator Utility"
    
    # 1. Get user input
    $passLenInput = Read-Host "Enter password length (default: 16)"
    
    # 2. Validate input
    $passLen = 16 # Default
    $numRegex = '^[1-9][0-9]*$'
    
    if ([string]::IsNullOrEmpty($passLenInput))
    {
        $passLen = 16
        Out-Info "Using default length: 16 characters."
    }
    elseif ($passLenInput -notmatch $numRegex) {
        Out-Error "Invalid input. Length must be a positive number."
        Wait-Script 2 
        return
    }
    elseif ([int]$passLenInput -gt 1024) {
        Out-Error "Length too large. Please choose a length under 1024."
        Wait-Script 2
        return
    }
    else {
        $passLen = [int]$passLenInput
    }
    
    # 3. Generate Password
    # Define the set of allowed characters
    $charSet = 'A-Za-z0-9!@#$%^&*'
    $charArray = $charSet.ToCharArray()
    
    Out-Info "Generating secure password..." 
    $password = -join (Get-Random -InputObject $charArray -Count $passLen)
    
    # 4. Display Password
    Out-Separator
    Write-Host "Your new password is:"
    Write-Host $password -ForegroundColor Yellow
    Out-Separator
    Out-Info "Copy this password to a safe place. It is not saved."
    Suspend-Script 
}

# --- Feature Function: Curf Remover (Safe File Cleaner) ---
function Start-CurfRemover {
    Out-Header "Curf Remover (Old File Cleaner)"
    
    # 1. Explain the tool and its risks
    Out-Info "This utility will find and delete files older than a specified number of days."
    Out-Error "WARNING: This is a destructive operation. Files are permanently deleted." 
    Out-Info "We will *only* target FILES and EMPTY FOLDERS. Non-empty folders are safe." 
    Out-Separator 
    
    # 2. Get user input
    $cleanPath = Read-Host "Enter the absolute path of the folder to clean"
    $daysInput = Read-Host "Delete files OLDER than how many days? (default: 15)"
    
    # 3. Validate input
    $days = 15
    if (-not [string]::IsNullOrEmpty($daysInput)) { 
        $days = [int]$daysInput
    }

    if (-not (Test-Path $cleanPath -PathType Container)) { 
        Out-Error "Path '$cleanPath' is not a valid directory. Aborting." 
        Wait-Script 2 
        return
    }
    
    # Validate 'days' is a number
    if ($daysInput -notmatch '^[0-9]+$') { 
        Out-Error "Invalid input. Days must be a number. Aborting." 
        Wait-Script 2 
        return
    }
    
    Out-Info "Searching for files in '$cleanPath' older than $days days..."
    $cutoffDate = (Get-Date).AddDays(-$days)

    # 4. Find files SAFELY
    $filesToDelete = Get-ChildItem -Path $cleanPath -File -Recurse | Where-Object { $_.LastWriteTime -lt $cutoffDate } 
    
    # Find *empty* directories
    $dirsToDelete = Get-ChildItem -Path $cleanPath -Directory -Recurse | Where-Object { 
        $_.GetFiles().Count -eq 0 -and $_.GetDirectories().Count -eq 0 -and $_.LastWriteTime -lt $cutoffDate 
    } | Sort-Object -Property FullName -Descending # Sort descending to delete subfolders first
    
    $fileCount = ($filesToDelete | Measure-Object).Count
    $dirCount = ($dirsToDelete | Measure-Object).Count
    $totalCount = $fileCount + $dirCount

    if ($totalCount -eq 0) { 
        Out-Success "No files or empty folders found older than $days days." 
        Wait-Script 2 
        return
    }
    
    # 5. The "Dry Run" / Confirmation
    Out-Separator
    Out-Info "Found $fileCount files and $dirCount empty folders to delete."
    Write-Host "You can review the list below:" 
    
    # Print the list for the user to see
    $filesToDelete | Select-Object -ExpandProperty FullName
    $dirsToDelete | Select-Object -ExpandProperty FullName
    
    Out-Separator
    Out-Error "This action is permanent. Are you sure?"
    $confirm = Read-Host "Type 'interactive' to confirm one-by-one, or 'ALL' to delete all" 
    
    # 6. The Execution
    switch ($confirm) {
        'interactive' {
            Out-Info "Starting interactive deletion..."
            if ($fileCount -gt 0) { 
                $filesToDelete | Remove-Item -Verbose -Confirm
            }
            if ($dirCount -gt 0) { 
                $dirsToDelete | Remove-Item -Verbose -Confirm
            }
            Out-Success "Interactive cleanup complete." 
        }
        'ALL' {
            Out-Info "Starting bulk deletion..."
            if ($fileCount -gt 0) { 
                $filesToDelete | Remove-Item -Verbose -Force
            }
            if ($dirCount -gt 0) { 
                $dirsToDelete | Remove-Item -Verbose -Force
            }
            Out-Success "Bulk cleanup complete." 
        }
        default {
            Out-Info "Invalid confirmation. Aborting. No files were deleted." 
        }
    }
    
    Suspend-Script
}

# --- Feature Function: User Creator ---
function Start-UserCreator {
    Out-Header "User Creator Utility"
    
    # 1. Permission Check
    # Check if the script is being run with Admin privileges. 
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) { 
        Out-Error "This action requires Administrator privileges." 
        Out-Info "Please run the script again as an Administrator." 
        Wait-Script 4
        return
    }
    
    Out-Info "Running with Administrator privileges. Ready to create user."
    # 2. Get user input 
    $username = Read-Host "Enter the new username"

    # 3. Validate input
    if ([string]::IsNullOrEmpty($username)) { 
        Out-Error "Username cannot be empty. Aborting." 
        Wait-Script 2 
        return
    }
    
    # Check if user already exists
    if (Get-LocalUser $username -ErrorAction SilentlyContinue) { 
        Out-Error "User '$username' already exists. Aborting." 
        Wait-Script 2 
        return
    }
    
    # Windows has different username rules, but we'll check for spaces.
    if ($username -match '\s') { 
        Out-Error "Invalid username. Spaces are not allowed." [cite: 65, 66]
        Wait-Script 4
        return
    }
    
    # 4. Confirmation and Execution
    Out-Info "You are about to create a new user named: $username"
    $confirm = Read-Host "Are you sure you want to proceed? (y/n)"
    
    if ($confirm -ne 'y') { 
        Out-Info "Aborting. No user was created." 
        Wait-Script 2 
        return
    }
    
    try {
        Out-Info "Please enter the password for '$username' now." [cite: 71, 72]
        $password = Read-Host -AsSecureString "Enter new password"
        
        # Create the user 
        New-LocalUser -Name $username -Password $password -FullName $username -Description "User created by toolkit" 
        Out-Success "Successfully created user '$username'." 
        Out-Info "Adding user to 'Users' group..."
        Add-LocalGroupMember -Group "Users" -Member $username
        Out-Success "User '$username' is ready."
    }
    catch {
        Out-Error "Failed to create user. $_" 
        Wait-Script 2 
        return
    }
    
    Suspend-Script
}

# --- Feature Function: Indexer (Batch File Renamer) ---
function Start-Indexer {
    Out-Header "Indexer (Batch File Renamer)"
    
    # 1. Get user input
    $targetDir = Read-Host "Enter the path to the directory with files to rename"
    $prefix = Read-Host "Enter a new prefix for the files (e.g., 'report-')"

    # 2. Validate input 
    if (-not (Test-Path $targetDir -PathType Container)) { 
        Out-Error "Directory '$targetDir' does not exist. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ([string]::IsNullOrEmpty($prefix)) { 
        Out-Info "No prefix entered. Using 'file-' as default." 
        $prefix = "file-" 
    }

    Out-Info "This will rename all files in '$targetDir' to '$prefix[number].[original_extension]'."
    Out-Error "WARNING: This action is permanent." 
    $confirm = Read-Host "Are you sure you want to proceed? (y/n)"
    
    if ($confirm -ne 'y') { 
        Out-Info "Aborting. No files were renamed." 
        Wait-Script 2 
        return
    }

    # 3. Execution
    $i = 1
    $renamedCount = 0
    
    # This loop is safe. It does not use 'cd'. 
    Get-ChildItem -Path $targetDir -File | ForEach-Object {
        
        # Get the extension (e.g., ".jpg") 
        $extension = $_.Extension # This includes the dot, e.g., ".jpg"
        
        $newName = ""
        # Check if the file has no extension
        if ([string]::IsNullOrEmpty($extension)) { 
            # Build new name with no extension
            $newName = "{0}{1:D3}" -f $prefix, $i 
        }
        else {
            # Build new name and *preserve* the original extension
            $newName = "{0}{1:D3}{2}" -f $prefix, $i, $extension 
        }

        #$newPath = Join-Path $targetDir $newName

        try {
            Rename-Item -Path $_.FullName -NewName $newName -Verbose -ErrorAction Stop 
            $renamedCount++
        }
        catch {
            Out-Error "Failed to rename '$($_.Name)'." 
        }
        
        $i++
    }
    
    Out-Separator
    Out-Success "Renaming complete. $renamedCount files were indexed."
    Suspend-Script 
}

# --- Feature Function: CSV Calculator ---
function Start-CsvCalculator {
    Out-Header "CSV Calculator"
    
    # 1. Dependency Check (PowerShell can do math, no 'bc' needed) 
    
    # 2. Get user input
    $csvFile = Read-Host "Enter the path to your CSV file"
    $hasHeader = Read-Host "Does this file have a header row? (y/n)"

    # 3. Validate input
    if (-not (Test-Path $csvFile -PathType Leaf)) { 
        Out-Error "File not found: '$csvFile'. Aborting." 
        Wait-Script 2 
        return
    }
    
    Out-Info "Parsing '$csvFile'..."
    Out-Separator
    
    $lineCount = 0
    
    # 4. The Loop
    $csvData = $null
    if ($hasHeader -eq 'y') { 
        # 'Import-Csv' automatically uses the first line as the header
        $csvData = Import-Csv -Path $csvFile 
    }
    else {
        # If no header, import as raw text and split
        $csvData = Get-Content $csvFile | ForEach-Object { $_ -split ',' }
    }

    foreach ($row in $csvData) { 
        try {
            $col1 = $null; $col2 = $null; $col3 = $null; $col4 = $null

            if ($hasHeader -eq 'y') {
                # Access by property name (assuming headers are 'col1', 'col2', etc.)
                # This part is tricky without knowing the headers. Let's assume headers are "Name", "ID", "Val1", "Val2"
                $col1 = $row.Name
                $col2 = $row.ID
                $col3 = [double]$row.Val1
                $col4 = [double]$row.Val2
            }
            else {
                # Access by array index
                $col1 = $row[0]
                $col2 = $row[1]
                $col3 = [double]$row[2]
                $col4 = [double]$row[3]
            }

            # Perform calculations (PowerShell does this natively) 
            $sum = $col3 + $col4
            $avg = $sum / 2

            # Print the results
            Write-Host "Name: $col1" 
            Write-Host "ID: $col2"
            Write-Host "Total: $sum" -ForegroundColor Green
            Write-Host "Average: $avg" -ForegroundColor Yellow
            Write-Host ""
            
            $lineCount++ 
        }
        catch {
            # Skip lines where col3/col4 aren't numbers
            Out-Info "Skipping malformed line..."
        }
    }
    
    Out-Separator
    Out-Success "Calculation complete. Processed $lineCount valid lines."
    Suspend-Script 
}

# --- Feature Function: Service Manager ---
function Start-ServiceManager {
    Out-Header "Service Manager"
    
    # 1. Permission Check
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) { 
        Out-Error "This action requires Administrator privileges." 
        Out-Info "Please run the script again as an Administrator." 
        Wait-Script 4
        return
    }
    
    # 2. Dependency Check (Not needed, Get-Service is built-in) 
    
    # 3. Get user input
    $serviceName = Read-Host "Enter the name of the service (e.g., 'WinRM', 'Spooler')"

    if ([string]::IsNullOrEmpty($serviceName)) { 
        Out-Error "No service name entered. Aborting." 
        Wait-Script 2 
        return
    }
    
    # 4. Check Status
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if (-not $service) {
        Out-Error "Could not find service '$serviceName'." 
        Wait-Script 2
        return
    }
    
    $status = $service.Status
    
    Out-Separator
    switch ($status) { 
        'Running' { 
            Out-Success "Service '$serviceName' is ACTIVE and RUNNING." 
            Out-Separator 
            $action = Read-Host "Do you want to (s)top or (r)estart this service? (any other key to exit)"
            switch ($action) {
                's' { 
                    Out-Info "Attempting to STOP '$serviceName'..."
                    Stop-Service $serviceName -Verbose
                    Out-Success "Service stopped." 
                }
                'r' {
                    Out-Info "Attempting to RESTART '$serviceName'..."
                    Restart-Service $serviceName -Verbose
                    Out-Success "Service restarted." 
                }
                default { Out-Info "No action taken."  }
            }
        } 
        'Stopped' { 
            Out-Info "Service '$serviceName' is INACTIVE (stopped)." 
            Out-Separator 
            $action = Read-Host "Do you want to (s)tart this service? (y/n)"
            if ($action -eq 'y') { 
                Out-Info "Attempting to START '$serviceName'..."
                Start-Service $serviceName -Verbose
                Out-Success "Service started." 
            }
            else { Out-Info "No action taken."  }
        } 
        default { # Covers 'Failed', 'Starting', 'Stopping' etc. [cite: 120, 126]
            Out-Error "Service '$serviceName' is in a '$status' state." 
            Out-Separator 
            Out-Info "Check 'Get-EventLog -LogName System' for details." 
            $action = Read-Host "Do you want to attempt a (r)estart? (y/n)" 
            if ($action -eq 'y') { 
                Out-Info "Attempting to RESTART '$serviceName'..."
                Restart-Service $serviceName -Verbose
                Out-Success "Restart attempted." 
            }
            else { Out-Info "No action taken."  }
        } 
    }
    
    Suspend-Script
}

# --- Feature Function: Online Image Extractor ---
function Start-ImageExtractor {
    Out-Header "Online Image Extractor"
    
    # 1. Dependency Check (Invoke-WebRequest is built-in) 
    
    # 2. Get user input
    $targetUrl = Read-Host "Enter the full website URL to scan (e.g., https://example.com)"
    $saveDir = Read-Host "Enter directory to save images (default: ~\Downloads\ExtractedImages)"

    # 3. Validate input
    if ([string]::IsNullOrEmpty($targetUrl)) { 
        Out-Error "No URL provided. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ([string]::IsNullOrEmpty($saveDir)) { 
        $saveDir = "$env:USERPROFILE\Downloads\ExtractedImages" 
    }
    
    # 4. Create directory and check for success
    try {
        New-Item -Path $saveDir -ItemType Directory -Force -ErrorAction Stop | Out-Null 
    }
    catch {
        Out-Error "Could not create save directory: $saveDir" 
        Out-Info "Please check permissions. Aborting."
        Wait-Script 3 
        return
    }
    
    Out-Info "Save directory set: $saveDir"
    Out-Info "Starting download from '$targetUrl'..."
    Out-Info "This may take some time..."
    
    # 5. Execution
    try {
        $page = Invoke-WebRequest -Uri $targetUrl -ErrorAction Stop
        
        # Find all image links on the page 
        $imageLinks = $page.Links | Where-Object { $_.href -match '\.(jpg|jpeg|png|gif)$' }
        
        foreach ($link in $imageLinks) {
            $imageUrl = $link.href
            # Handle relative URLs
            if ($imageUrl -notlike "http*") {
                $imageUrl = [System.Uri]::new([System.Uri]$targetUrl, $imageUrl).AbsoluteUri
            }
            
            $fileName = [System.IO.Path]::GetFileName($imageUrl)
            $outPath = Join-Path $saveDir $fileName
            
            Out-Info "Downloading $fileName..."
            Invoke-WebRequest -Uri $imageUrl -OutFile $outPath
        }
    }
    catch {
        Out-Error "Failed to download page or images: $($_.Exception.Message)"
    }
    
    # 6. Report results
    $filesFound = (Get-ChildItem -Path $saveDir -File -Filter "*.jpg" -ErrorAction SilentlyContinue).Count + `
                  (Get-ChildItem -Path $saveDir -File -Filter "*.jpeg" -ErrorAction SilentlyContinue).Count + `
                  (Get-ChildItem -Path $saveDir -File -Filter "*.png" -ErrorAction SilentlyContinue).Count + `
                  (Get-ChildItem -Path $saveDir -File -Filter "*.gif" -ErrorAction SilentlyContinue).Count
    
    Out-Separator
    if ($filesFound -gt 0) { 
        Out-Success "Download complete. Saved $filesFound images to '$saveDir'." 
    }
    else { 
        Out-Info "Scan complete. No images matching (jpg, jpeg, png, gif) were found on that page." 
        Remove-Item -Path $saveDir -ErrorAction SilentlyContinue 
    }
    
    Suspend-Script
}

# --- Feature Function: TarBall Mailer ---
function Start-TarBallMailer {
    Out-Header "TarBall Mailer (Backup & Notify)"
    
    # 1. Dependency Checks (Compress-Archive and Send-MailMessage are built-in) [cite: 141, 143]
    Out-Info "This tool uses 'Compress-Archive' and 'Send-MailMessage'." 
    Out-Info "Send-MailMessage requires a configured SMTP server to work." 
    
    # 2. Get user input
    $srcDir = Read-Host "Enter the full path of the SOURCE directory to backup"
    $destDir = Read-Host "Enter the full path of the DESTINATION directory for the backup"
    $emailAddr = Read-Host "Enter the email address for notification"
    
    # --- IMPORTANT: SMTP Configuration ---
    # Send-MailMessage needs an SMTP server. This must be set.
    $smtpServer = "smtp.your-email-provider.com" # e.g., smtp.gmail.com
    $fromEmail = "your-script-email@gmail.com"
    # ------------------------------------

    # 3. Validate input
    if (-not (Test-Path $srcDir -PathType Container)) { 
        Out-Error "Source directory '$srcDir' does not exist. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ($emailAddr -notmatch '^[^@]+@[^@]+\.[^@]+$') { 
        Out-Error "Invalid email address format. Aborting." 
        Wait-Script 2 
        return
    }
    
    try {
        New-Item -Path $destDir -ItemType Directory -Force -ErrorAction Stop | Out-Null 
    }
    catch {
        Out-Error "Could not create destination directory '$destDir'." 
        Out-Info "Please check permissions. Aborting." 
        Wait-Script 3
        return
    }
    
    # 4. Prepare for archive
    $srcFolderName = (Get-Item $srcDir).Name
    $backupFilename = "{0}_{1}.zip" -f $srcFolderName, (Get-Date -Format "yyyy-MM-dd_HHmmss")
    $fullBackupPath = Join-Path $destDir $backupFilename
    
    Out-Info "Preparing to archive '$srcDir'..."
    Out-Info "Target file: $fullBackupPath"
    
    # 5. Execution (Create Archive) 
    # PowerShell's native compression is .zip, not .tar.gz 
    try {
        Compress-Archive -Path "$srcDir\*" -DestinationPath $fullBackupPath -ErrorAction Stop 
        
        # The 'Compress-Archive' command was successful
        Out-Success "Backup archive created successfully!" 
        Out-Separator 
        Out-Info "Sending email notification to $emailAddr..."
        
        # 6. Send Email
        $subject = "[Backup SUCCESS] $srcFolderName"
        $body = "Backup of '$srcDir' was successfully created.
        
File: $fullBackupPath
Host: $env:COMPUTERNAME
Date: $(Get-Date)"

        # Send the email
        Send-MailMessage -From $fromEmail -To $emailAddr -Subject $subject -Body $body -SmtpServer $smtpServer 
        
        Out-Success "Email notification sent."
    }
    catch {
        # The 'Compress-Archive' or 'Send-MailMessage' command failed 
        Out-Error "Operation FAILED: $($_.Exception.Message)" 
        Out-Info "No email notification will be sent." 
        Remove-Item -Path $fullBackupPath -ErrorAction SilentlyContinue
        Wait-Script 2
        return
    }
    
    Suspend-Script
}

# --- Feature Function: Term/Phase Fetcher (Select-String wrapper) ---
function Start-TermFetcher {
    Out-Header "Term/Phase Fetcher (Select-String)"
    
    # 1. Dependency Check (Select-String is built-in) 
    
    # 2. Get user input
    $searchTerm = Read-Host "Enter the word or phrase to search for"
    $searchDir = Read-Host "Enter directory to search in (default: current directory)"
    $caseInsensitive = Read-Host "Make search case-insensitive? (y/n)"

    # 3. Validate input
    if ([string]::IsNullOrEmpty($searchTerm)) { 
        Out-Error "No search term provided. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ([string]::IsNullOrEmpty($searchDir)) { 
        $searchDir = ".\"
        Out-Info "Using current directory for search." [cite: 161, 162]
    }
    
    if (-not (Test-Path $searchDir -PathType Container)) { 
        Out-Error "Directory '$searchDir' does not exist. Aborting." 
        Wait-Script 2 
        return
    }
    
    # 4. Build 'Select-String' command options
    $ssParams = @{
        Pattern = $searchTerm
        Path = "$searchDir\*"
        Recurse = $true
        ErrorAction = 'SilentlyContinue'
    }
    
    if ($caseInsensitive -eq 'y') { 
        $ssParams.CaseSensitive = $false
        Out-Info "Running case-insensitive search..."
    }
    else {
        $ssParams.CaseSensitive = $true
        Out-Info "Running case-sensitive search..."
    }

    Out-Info "Searching for '$searchTerm' in '$searchDir'..."
    Out-Separator
    
    # 5. Execution 
    $results = Select-String @ssParams
    
    # 6. Report results
    Out-Separator 
    if ($results) {
        # 'Select-String' automatically highlights, so just output
        $results | Format-List Path, LineNumber, Line
        Out-Success "Search complete. Matches found." 
    }
    else {
        Out-Info "Search complete. No matches found for '$searchTerm'." 
    }

    Suspend-Script
}

# --- Feature Function: Network Diagnostic Tool ---
function Start-NetworkDiagnostics {
    Out-Header "Network Diagnostic Tool"
    
    # 1. Dependency Checks (Test-Connection, Get-NetRoute, Resolve-DnsName are built-in) [cite: 171, 172, 174]
    
    # 2. Get user input
    $domain = Read-Host "Enter a domain to test (default: google.com)"
    if ([string]::IsNullOrEmpty($domain)) { 
        $domain = "google.com" 
    }
    
    Out-Info "Running 3-step network diagnostic..."
    Out-Separator
    
    $allPassed = $true
    
    # --- Step 1: Test Gateway (Local Network) ---
    $gatewayIP = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Sort-Object RouteMetric | Select-Object -First 1).NextHop
    
    if ([string]::IsNullOrEmpty($gatewayIP)) { 
        Out-Error "Could not determine gateway IP. Skipping Step 1." 
        $allPassed = $false 
    }
    else {
        Out-Info "Step 1/3: Pinging gateway ($gatewayIP)..."
        # -Count 3 = send 3 packets
        if (Test-Connection -ComputerName $gatewayIP -Count 3 -Quiet -ErrorAction SilentlyContinue) { 
            Out-Success "  [PASS] Gateway is reachable." 
        }
        else { 
            Out-Error "  [FAIL] Gateway is NOT reachable." 
            $allPassed = $false 
        }
    }
    
    # --- Step 2: Test Internet (External IP) ---
    Out-Info "Step 2/3: Pinging public DNS (8.8.8.8)..."
    if (Test-Connection -ComputerName "8.8.8.8" -Count 3 -Quiet -ErrorAction SilentlyContinue) { 
        Out-Success "  [PASS] Public internet is reachable." 
    }
    else { 
        Out-Error "  [FAIL] Public internet is NOT reachable." 
        $allPassed = $false 
    }

    # --- Step 3: Test DNS (Name Resolution) ---
    Out-Info "Step 3/3: Resolving domain ($domain)..."
    try {
        $dnsResult = Resolve-DnsName -Name $domain -ErrorAction Stop 
        Out-Success "  [PASS] DNS resolution is working." 
        $dnsResult | Format-Table Name, Type, IPAddress 
    }
    catch {
        Out-Error "  [FAIL] DNS resolution FAILED." 
        $allPassed = $false 
    }
    
    # --- Final Report ---
    Out-Separator
    if ($allPassed) { 
        Out-Success "All network checks passed. Connectivity is good! 🚀" 
    }
    else { 
        Out-Error "One or more network checks failed. Please review." [cite: 188, 189]
    }
    
    Suspend-Script
}

# --- Feature Function: System Health Dashboard ---
function Start-SystemHealth {
    Out-Header "System Health Dashboard"
    
    # 1. Dependency Checks (All commands are built-in) [cite: 190, 191, 192, 193]
    
    $hostName = $env:COMPUTERNAME
    
    # 2. Clear screen to create a "dashboard" effect
    Clear-Host
    Out-Header "System Health Report for: $hostName"

    # 3. Show Uptime & Load Average
    Write-Host "--- Uptime & Load ---" -ForegroundColor Cyan
    $os = Get-CimInstance Win32_OperatingSystem
    $uptime = (Get-Date) - $os.LastBootUpTime
    Write-Host "Uptime: $($uptime.Days) days, $($uptime.Hours) hours, $($uptime.Minutes) minutes"
    Get-CimInstance Win32_Processor | Format-Table Name, LoadPercentage
    Write-Host ""

    # 4. Show Memory Usage
    Write-Host "--- Memory Usage ---" -ForegroundColor Cyan 
    $mem = Get-CimInstance Win32_OperatingSystem
    $totalMB = [math]::Round($mem.TotalVisibleMemorySize / 1024)
    $freeMB = [math]::Round($mem.FreePhysicalMemory / 1024)
    $usedMB = $totalMB - $freeMB
    $percentFree = [math]::Round(($freeMB / $totalMB) * 100, 2)
    Write-Host "Total: $totalMB MB"
    Write-Host "Used:  $usedMB MB"
    Write-Host "Free:  $freeMB MB ($percentFree % free)"
    Write-Host "" 
    
    # 5. Show Disk Usage
    Write-Host "--- Filesystem Disk Usage ---" -ForegroundColor Cyan
    Get-Volume | Format-Table DriveLetter, FileSystemLabel, FileSystem, @{N="Size (GB)"; E={[math]::Round($_.Size / 1GB, 2)}}, @{N="Free (GB)"; E={[math]::Round($_.SizeRemaining / 1GB, 2)}}, @{N="% Free"; E={[math]::Round(($_.SizeRemaining / $_.Size) * 100, 2)}}
    Write-Host ""
    
    Out-Separator
    Suspend-Script
}

# --- Feature Function: Log File Analyzer ---
function Start-LogAnalyzer {
    Out-Header "Log File Analyzer (Windows Events)" 
    
    # 1. Dependency Checks (Get-WinEvent is built-in) [cite: 196, 197]
    
    # 2. Get user input
    $logName = Read-Host "Enter Log Name (e.g., Application, System, Security)"
    $logLevel = Read-Host "Enter Log Level (e.g., Error, Warning, Information)"
    $lineCount = Read-Host "How many recent lines to show? (default: 10)"

    # 3. Validate input
    try {
        Get-WinEvent -ListLog $logName -ErrorAction Stop | Out-Null
    }
    catch {
        Out-Error "Log file (LogName) not found: '$logName'. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ([string]::IsNullOrEmpty($logLevel)) { 
        Out-Error "No search term (Log Level) provided. Aborting." 
        Wait-Script 2 
        return
    }
    
    if ([string]::IsNullOrEmpty($lineCount)) { 
        $lineCount = 10 
    }
    elseif ($lineCount -notmatch '^[0-9]+$') { 
        Out-Error "Invalid input. Lines must be a number." 
        Wait-Script 2 
        return
    }
    
    Out-Info "Searching '$logName' log for the $lineCount most recent '$logLevel' events..."
    Out-Separator
    
    # 4. Execution
    try {
        $results = Get-WinEvent -LogName $logName -FilterXPath "*[System[Level='$logLevel']]" -MaxEvents $lineCount -ErrorAction Stop 
        
        # 5. Report Results
        if (-not $results) { 
            Out-Info "Search complete. No matches found." 
        }
        else { 
            # Format results for readability
            $results | Format-Table TimeCreated, Id, ProviderName, Message -Wrap
            Out-Separator
            Out-Success "Search complete. Showing most recent matches." 
        }
    }
    catch {
        Out-Error "An error occurred: $($_.Exception.Message)" 
    }
    
    Suspend-Script
}

# =============================================================================
# MAIN MENU & SCRIPT LOGIC CENTER (The Engine)
# =============================================================================

# Function to display the main menu
function Show-MainMenu {
    Clear-Host
    
    # Comment off the lines below to disable the banner.
#    $banner = @'
#++======================================================================++
#| ╔═╗╔═╗╔═══╗╔═╗ ╔╗╔═══╗╔╗╔═══╗     ╔════╗╔═══╗╔═══╗╔╗   ╔╗╔═╗╔══╗╔════╗ |
#| ╚╗╚╝╔╝║╔══╝║║╚╗║║║╔═╗║║║║╔═╗║     ║╔╗╔╗║║╔═╗║║╔═╗║║║   ║║║╔╝╚╣╠╝║╔╗╔╗║ |
#|  ╚╗╔╝ ║╚══╗║╔╗╚╝║║║ ║║╚╝║╚══╗     ╚╝║║╚╝║║ ║║║║ ║║║║   ║╚╝╝  ║║ ╚╝║║╚╝ |
#|  ╔╝╚╗ ║╔══╝║║╚╗║║║║ ║║  ╚══╗║       ║║  ║║ ║║║║ ║║║║ ╔╗║╔╗║  ║║   ║║   |
#| ╔╝╔╗╚╗║╚══╗║║ ║║║║╚═╝║  ║╚═╝║      ╔╝╚╗ ║╚═╝║║╚═╝║║╚═╝║║║║╚╗╔╣╠╗ ╔╝╚╗  |
#| ╚═╝╚═╝╚═══╝╚╝ ╚═╝╚═══╝  ╚═══╝      ╚══╝ ╚═══╝╚═══╝╚═══╝╚╝╚═╝╚══╝ ╚══╝  |
#|                        POWERSHELL EDITION                              |
#++======================================================================++
#'@   
#    Write-Host $banner -ForegroundColor Black -BackgroundColor White
    Write-Host "[##] ... XENO'S TOOLKIT ... [##]" -ForegroundColor Black -BackgroundColor Green
    Write-Host "Select an option to proceed:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Folder Organizer"
    Write-Host "2. Password Generator"
    Write-Host "3. Curf Remover (Safe File Cleaner)"
    Write-Host "4. User Creation" 
    Write-Host "5. Indexer (Batch File Renamer)"
    Write-Host "6. CSV Calculator"
    Write-Host "7. Service Manager" 
    Write-Host "8. Online Image Extractor"
    Write-Host "9. TarBall Mailer (.ZIP)" 
    Write-Host "10. Term/Phase Fetcher"
    Write-Host "11. Network Diagnostic Tool" 
    Write-Host "12. System Health Dashboard"
    Write-Host "13. Log File Analyzer" 
    Write-Host ""
    Write-Host "q. Quit" -ForegroundColor Red 
    Out-Separator
}

# --- Main Loop ---
# This loop runs forever until the user presses 'q'
:MainMenu while ($true) {
    Show-MainMenu
    $choice = Read-Host "Enter your choice"
    
    switch ($choice) { 
        '1' { Start-FolderOrganizer }
        '2' { Start-PasswordGenerator }
        '3' { Start-CurfRemover }
        '4' { Start-UserCreator }
        '5' { Start-Indexer } 
        '6' { Start-CsvCalculator } 
        '7' { Start-ServiceManager }
        '8' { Start-ImageExtractor }
        '9' { Start-TarBallMailer }
        '10' { Start-TermFetcher }
        '11' { Start-NetworkDiagnostics }
        '12' { Start-SystemHealth }
        '13' { Start-LogAnalyzer }
        'q' {
            Write-Host "Ending Process!"
            break MainMenu # This command exits the 'while true' loop
            }
        default {
            Out-Error "Invalid option '$choice'. Please try again." 
            Wait-Script 2
                }
    }
}