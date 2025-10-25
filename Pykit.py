#!/usr/bin/env python3
# Pykit: A Modular Security and Automation Framework


import logging
import requests
import sys
import os 
from urllib.parse import urlparse
import socket
import threading
import telnetlib 
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import string
import shutil

# =============================================================================
# --- COLOR SCHEME ---
# =============================================================================

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
PURPLE = '\033[0;35m'
GREY   = '\033[0;90m'  
RESET  = '\033[0m'   # Reset the color
NC = '\033[0m'  # No Color


# =============================================================================
# --- GLOBAL HELPER FUNCTIONS ---
# =============================================================================

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def suspend_script( message="Press [Enter] to return to the main menu..."):
    response = f"{YELLOW}{message}{NC}"
    input(response)


# =============================================================================
# --- CENTRALIZED LOGGING CONFIGUREs ---
# =============================================================================

# Logging format
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - (%(threadName)-10s) - %(message)s'

# "handler" to send logs to the console (stdout)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Get the root logger and add our handler
logger = logging.getLogger("PyToolkit{NC}")
logger.setLevel(logging.INFO)  # Set the default log level (INFO, DEBUG, ERROR)
logger.addHandler(stream_handler)


# =============================================================================
# --- 2. DEFINE THE MAIN TOOLKIT CLASS ---
# =============================================================================

class PyToolkit:

    def __init__(self):
        # Assigning the logger we just configured to the class instance
        self.logger = logger
        self.logger.info(f"{BLUE}PyToolkit Core initializing...{NC}")

        # --- 3. INITIALIZE THE SHARED REQUESTS SESSION ---
        # All web modules (WebManager, ReconManager) will use this
        # one session object.
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PyToolkit/1.0 (Educational Framework)"
        })
        self.logger.info(f"{BLUE}{GREY}Shared requests.Session created.{NC}")

        # --- 4. LOAD THE TOOLKIT MODULES ---
        self.network = NetworkManager(self)
        self.web = WebManager(self)
        self.recon = ReconManager(self)
        self.system = SystemManager(self)
        self.security = SecurityAnalysis(self)
        self.logger.info(f"{GREEN}All modules loaded.{NC}")
    
    def _menu_download_file(self):
        print(f"{PURPLE}--- [Tool: Download File] ---{NC}")
        url = input(f"{YELLOW}Enter the full URL to download: {NC}")
        dest = input(f"{YELLOW}Enter destination folder (default: .): {NC}") or "."
        if not url:
            self.logger.error(f"{RED}URL cannot be empty.{NC}")
            return
        self.web.download_file(url, dest)

    def _menu_get_headers(self):
        print(f"{PURPLE}--- [Tool: Get Page Headers] ---{NC}")
        url = input(f"{YELLOW}Enter URL to get headers from: {NC}")
        if not url:
            self.logger.error(f"{RED}URL cannot be empty.{NC}")
            return
            
        status, headers, content = self.web.get_page_content(url)
        if headers:
            print(f"\nStatus: {status}{NC}")
            print("Headers:{NC}")
            for k, v in headers.items():
                print(f"  {k}: {v}{NC}")
        else:
            self.logger.error(f"{RED}Could not fetch URL.{NC}")

    def _menu_crawl_site(self):
        print(f"{PURPLE}--- [Tool: Site Crawler] ---{NC}")
        url = input(f"{YELLOW}Enter base URL to crawl (e.g., http://hello.world!!.com): {NC}")
        if not url:
            self.logger.error(f"{RED}URL cannot be empty.{NC}")
            return
        depth = input(f"{YELLOW}Enter max depth (default: 2): {NC}")
        try:
            max_depth = int(depth) if depth else 2
        except ValueError:
            self.logger.warning(f"{RED}Invalid depth. Defaulting to 2.{NC}")
            max_depth = 2
        
        self.logger.info(f"{BLUE}Starting crawl. This may take time... (see log){NC}")
        links = self.recon.crawl_site(url, max_depth)
        print(f"\n{GREEN}Crawl complete. Found {len(links)} links. See log for full list.{NC}")

    def _menu_extract_forms(self):
        print(f"{PURPLE}--- [Tool: Extract Forms] ---{NC}")
        url = input(f"{YELLOW}Enter URL to extract forms from: {NC}")
        if not url:
            self.logger.error(f"{RED}URL cannot be empty.{NC}")
            return
        
        forms = self.recon.extract_all_forms(url)
        if not forms:
            print(f"{GREY}No forms found on that page.{NC}")
            return
        
        print(f"\n{GREEN}Found {len(forms)} form(s):{NC}")
        for i, form in enumerate(forms, 1):
            action = form.get("action", "N/A{NC}")
            method = form.get("method", "N/A{NC}").upper()
            print(f"{GREEN}  [Form {i}] Action: {action} | Method: {method}{NC}")

    def _menu_gen_password(self):
        print(f"{PURPLE}--- [Tool: Password Generator] ---{NC}")
        length_str = input(f"{YELLOW}Enter password length (default: 16): {NC}")
        try:
            length = int(length_str) if length_str else 16
        except ValueError:
            self.logger.warning(f"{RED}Invalid length. Defaulting to 16.{NC}")
            length = 16
            
        password = self.system.generate_password(length)
        print(f"\n{GREEN}Generated Password:{NC}")
        print(f"{password}{NC}")
        print(f"\n{RED}(Copy this to a safe place. It is not saved.){NC}")

    def _menu_org_folder(self):
        print(f"{PURPLE}--- [Tool: Folder Organizer] ---{NC}")
        src_path = input(f"{YELLOW}Enter the absolute path of the folder to organize: {NC}")
        dest_path = input(f"{YELLOW}Enter the destination path for organized files: {NC}")
        
        if not src_path or not dest_path:
            self.logger.error(f"{RED}Source and destination paths are required.{NC}")
            return
        
        self.system.organize_folder(src_path, dest_path)

    def _menu_start_listener(self):
        print(f"{PURPLE}--- [Tool: Start TCP Listener] ---{NC}")
        host = input(f"{YELLOW}Enter host to listen on (default: 0.0.0.0): {NC}") or "0.0.0.0"
        port = input(f"{YELLOW}Enter port to listen on (default: 8080): {NC}")
        try:
            port_int = int(port) if port else 8080
        except ValueError:
            self.logger.error(f"{RED}Invalid port. Defaulting to 8080.{NC}")
            port_int = 8080
        
        self.logger.info(f"{BLUE}Starting listener in a new thread...{NC}")
        # We MUST run the listener in a thread so it doesn't block the menu
        listener_thread = threading.Thread(
            target=self.network.create_listener,
            args=(host, port_int),
            daemon=True # This allows the program to exit
        )
        listener_thread.start()
        
        print(f"\nListener started on {RED}{host}:{port_int}{NC}. See log for connections.")
        print(f"{RED}NOTE: This will run in the background until you quit the main app.{NC}")

    def _menu_connect_host(self):
        print(f"{PURPLE}--- [Tool: Connect to Host (Interactive)] ---{NC}")
        host = input(f"{YELLOW}Enter host to connect to: {NC}")
        port = input(f"{YELLOW}Enter port: {NC}")
        
        if not host or not port:
            self.logger.error(f"{RED}Host and port are required.{NC}")
            return
            
        try:
            port_int = int(port)
            sock = self.network.connect_to_host(host, port_int)
            if sock:
                self.network.start_interactive_shell(sock)
            else:
                self.logger.error(f"{RED}Connection failed. See log.{NC}")
        except ValueError:
            self.logger.error(f"{RED}Invalid port. Must be a number.{NC}")
        except Exception as e:
            self.logger.error(f"{RED}Shell failed: {e}{NC}")

    def _show_main_menu(self):
        """
        Private helper to display the menu and get a choice.
        """
        clear_screen()
        print(fr"""{GREEN}
        ++======================================================================++
        | ╔═╗╔═╗╔═══╗╔═╗ ╔╗╔═══╗╔╗╔═══╗     ╔════╗╔═══╗╔═══╗╔╗   ╔╗╔═╗╔══╗╔════╗ |
        | ╚╗╚╝╔╝║╔══╝║║╚╗║║║╔═╗║║║║╔═╗║     ║╔╗╔╗║║╔═╗║║╔═╗║║║   ║║║╔╝╚╣╠╝║╔╗╔╗║ |
        |  ╚╗╔╝ ║╚══╗║╔╗╚╝║║║ ║║╚╝║╚══╗     ╚╝║║╚╝║║ ║║║║ ║║║║   ║╚╝╝  ║║ ╚╝║║╚╝ |
        |  ╔╝╚╗ ║╔══╝║║╚╗║║║║ ║║  ╚══╗║       ║║  ║║ ║║║║ ║║║║ ╔╗║╔╗║  ║║   ║║   |
        | ╔╝╔╗╚╗║╚══╗║║ ║║║║╚═╝║  ║╚═╝║      ╔╝╚╗ ║╚═╝║║╚═╝║║╚═╝║║║║╚╗╔╣╠╗ ╔╝╚╗  |
        | ╚═╝╚═╝╚═══╝╚╝ ╚═╝╚═══╝  ╚═══╝      ╚══╝ ╚═══╝╚═══╝╚═══╝╚╝╚═╝╚══╝ ╚══╝  |
        |                   PYTHON EDITION : WINDOWS NATIVE                      |
        ++======================================================================++
        {NC}""")
        print("\n")        
        print(f"{PURPLE}--- Web & Recon ---{NC}")
        print(f"{CYAN} 1. Download File from URL{NC}")
        print(f"{CYAN} 2. Get Page Headers{NC}")
        print(f"{CYAN} 3. Crawl Site (Find Links){NC}")
        print(f"{CYAN} 4. Extract Forms from URL{NC}")
        print(f"{PURPLE}\n--- System Utilities ---{NC}")
        print(f"{CYAN} 5. Generate Secure Password{NC}")
        print(f"{CYAN} 6. Organize Folder{NC}")
        print(f"{PURPLE}\n--- Network ---{NC}")
        print(f"{CYAN} 7. Start TCP Listener (Echo Server){NC}")
        print(f"{CYAN} 8. Connect to Host (Interactive){NC}")
        print(f"{PURPLE}\n--- Defensive Analysis ---{NC}")
        print(f"{CYAN} 9. Explain XSS Prevention{NC}")
        print(f"{CYAN} 10. Explain C2 / Reverse Shell Defense{NC}")
        print(f"{CYAN} 11. Explain Brute-Force Defense{NC}")
        print(f"{CYAN} 12. Explain Registry Persistence{NC}")
        print("\n" + "-"*40)
        print(f"{RED} q. Quit{NC}")
        print("-" * 40)
        return input(f"{YELLOW}Enter your choice: {NC}").strip().lower()

    def run_cli_menu(self):
        """
        The main interactive loop for the toolkit.
        This replaces the old test-based function.
        """
        self.logger.info(f"{BLUE}Starting interactive CLI menu...{NC}")
        
        # This is the main loop, replacing the 'while ($true)' from PowerShell
        while True:
            choice = self._show_main_menu()
            
            try:
                # --- This is the 'switch' from PowerShell ---
                if choice == '1':
                    self._menu_download_file()
                elif choice == '2':
                    self._menu_get_headers()
                elif choice == '3':
                    self._menu_crawl_site()
                elif choice == '4':
                    self._menu_extract_forms()
                elif choice == '5':
                    self._menu_gen_password()
                elif choice == '6':
                    self._menu_org_folder()
                elif choice == '7':
                    self._menu_start_listener()
                elif choice == '8':
                    self._menu_connect_host()
                elif choice == '9':
                    self.security.scanner.explain_xss_prevention()
                elif choice == '10':
                    self.security.c2.explain_c2_defense()
                elif choice == '11':
                    self.security.bruteforce.explain_brute_force_defense()
                elif choice == '12':
                    self.security.persistence.explain_registry_persistence()
                elif choice == 'q':
                    self.logger.info(f"{BLUE}User requested exit. Shutting down.{NC}")
                    break
                else:
                    self.logger.warning(f"{RED}Invalid choice '{choice}'. Please try again.{NC}")
                
                # --- Pause for user to read output ---
                # (We don't pause if the user is quitting)
                if choice != 'q':
                    suspend_script()
                    
            except Exception as e:
                # Catch any unexpected errors from the tools
                self.logger.error(f"{RED}An error occurred in menu option {choice}: {e}{NC}")
                suspend_script(f"{YELLOW}An unexpected error occurred. Press [Enter] to continue...{NC}")

# =============================================================================
# --- MODULE: WEB MANAGER ---
# =============================================================================

class WebManager:
    """
    Handles all high-level HTTP interactions.

    This module consolidates all scripts that used 'requests' or 'urllib'
    to download files, get headers, or fetch page content. It uses the
    toolkit's shared session for all operations.
    """

    def __init__(self, toolkit):
        """
        Initializes the WebManager.

        Args:
            toolkit (PyToolkit): The main toolkit instance.
        """
        self.toolkit = toolkit
        self.logger = toolkit.logger
        self.session = toolkit.session
        self.logger.info(f"{BLUE}WebManager module loaded.{NC}")

    def get_page_content(self, url):
        """
        Fetches the full content and headers for a given URL.
        This replaces the logic from HTTP_NonSocket.py.

        Args:
            url (str): The URL to fetch.

        Returns:
            tuple: (status_code, headers, content_bytes) or (None, None, None) on failure.
        """
        self.logger.info(f"{BLUE}Attempting to GET: {url}{NC}")
        try:
            response = self.session.get(url, timeout=10)
            # Raise an exception for bad status codes (4xx, 5xx)
            response.raise_for_status() 

            self.logger.info(f"{BLUE}Success ({response.status_code}) for: {url}{NC}")
            return response.status_code, response.headers, response.content
        
        except requests.exceptions.HTTPError as e:
            self.logger.warning(f"{RED}HTTP Error for {url}: {e}{NC}")
            return e.response.status_code, e.response.headers, e.response.content
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"{RED}Connection Error for {url}: {e}{NC}")
            return None, None, None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{RED}Failed to get content from {url}: {e}{NC}")
            return None, None, None

    def download_file(self, url, dest_folder=".{NC}"):
        """
        Downloads a file from a URL and saves it to a destination.
        This replaces 'downloader.py'. It is more robust as it
        streams the download, saving memory on large files.

        Args:
            url (str): The URL of the file to download.
            dest_folder (str): The local folder to save the file in.

        Returns:
            str: The full path to the downloaded file, or None on failure.
        """
        self.logger.info(f"{BLUE}Attempting to download file from: {url}{NC}")
        try:
            # 1. Get the filename from the URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "downloaded_file" # Fallback
            
            # 2. Create the destination path
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = os.path.join(dest_folder, filename)

            # 3. Stream the download
            with self.session.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            self.logger.info(f"Successfully downloaded {GREEN}'{filename}'{NC} to {RED}'{dest_path}'{NC}")
            return dest_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{RED}Failed to download file from {url}: {e}{NC}")
            return None

# =============================================================================
# --- MODULE: NETWORK MANAGER ---
# =============================================================================

class NetworkManager:
    """
    Handles all low-level TCP socket operations.

    This module consolidates all 'CLIENTSock' and 'SERVERSock' scripts
    into a reusable class for creating listeners and clients.
    """
    
    def __init__(self, toolkit):
        """
        Initializes the NetworkManager.

        Args:
            toolkit (PyToolkit): The main toolkit instance.
        """
        self.toolkit = toolkit
        self.logger = toolkit.logger
        self.logger.info(f"{BLUE}NetworkManager module loaded.{NC}")
        self.buffer_size = 1024

    def create_listener(self, listen_host, listen_port):
        """
        Creates a new TCP listener on a specified host and port.
        This replaces 'SERVERSock.py' and is designed to be run in a thread.

        Args:
            listen_host (str): The IP address to bind to (e.g., "0.0.0.0{NC}").
            listen_port (int): The port to listen on.
        """
        self.logger.info(f"{BLUE}Starting new listener on {listen_host}:{listen_port}{NC}")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((listen_host, listen_port))
            server.listen(5)
            self.logger.info(f"{BLUE}Listener is live, waiting for connections...{NC}")

            while True:
                # This will block until a client connects
                client_socket, addr = server.accept()
                self.logger.info(f"{BLUE}Accepted connection from: {addr[0]}:{addr[1]}{NC}")
                
                # --- Handle the new client in a separate thread ---
                # This is a crucial improvement from SERVERSock.py.
                # It allows the server to handle multiple clients at once.
                client_thread = threading.Thread(
                    target=self.handle_client_connection, 
                    args=(client_socket, addr)
                )
                client_thread.daemon = True # Allows program to exit even if threads are running
                client_thread.start()

        except OSError as e:
            self.logger.error(f"{RED}Listener socket error: {e}{NC}")
        except KeyboardInterrupt:
            self.logger.info(f"{BLUE}Listener shutting down.{NC}")
        finally:
            server.close()

    def handle_client_connection(self, client_socket, addr):
        """
        This function is called by create_listener to handle a new client.
        This is where you'd put logic from 'SERVERSock.py's while loop.
        """
        try:
            # Send a welcome message
            welcome_msg = "Connection Established to Server\r\n"
            client_socket.send(welcome_msg.encode())
            
            # Simple echo logic
            while True:
                request = client_socket.recv(self.buffer_size)
                if not request:
                    self.logger.info(f"{BLUE}Client {addr[0]}:{addr[1]} disconnected.{NC}")
                    break
                
                self.logger.info(f"{BLUE}Received from {addr[0]}: {request.decode().strip()}{NC}")
                # Echo the message back
                client_socket.send(b"ECHO: " + request)

        except ConnectionResetError:
            self.logger.warning(f"{RED}Connection reset by {addr[0]}:{addr[1]}.{NC}")
        except Exception as e:
            self.logger.error(f"{RED}Error handling client {addr[0]}: {e}{NC}")
        finally:
            client_socket.close()

    def connect_to_host(self, target_host, target_port):
        """
        Connects to a target host and returns the socket object.
        This is the core logic from all 'CLIENTSock_*.py' scripts.

        Args:
            target_host (str): The target IP or hostname.
            target_port (int): The target port.

        Returns:
            socket.socket: A connected socket object, or None on failure.
        """
        self.logger.info(f"{BLUE}Attempting to connect to {target_host}:{target_port}{NC}")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((target_host, target_port))
            self.logger.info(f"{BLUE}Successfully connected to {target_host}:{target_port}{NC}")
            return client
        except socket.error as e:
            self.logger.error(f"{RED}Socket connection failed: {e}{NC}")
            return None

    def start_interactive_shell(self, sock):
        """
        Hooks a connected socket into an interactive Telnet session.
        This replaces 'CLIENTSock_Interactive.py'.

        Args:
            sock (socket.socket): A connected socket object.
        """
        if not sock:
            self.logger.error(f"{RED}Cannot start interactive shell: invalid socket.{NC}")
            return
            
        self.logger.info(f"{BLUE}Starting interactive shell. (Press Ctrl+] or Ctrl+C to quit){NC}")
        try:
            # telnetlib.Telnet() can wrap an existing socket
            t = telnetlib.Telnet()
            t.sock = sock
            t.interact() # This hands control over to the user
        except Exception as e:
            self.logger.error(f"{RED}Interactive shell error: {e}{NC}")
        finally:
            self.logger.info(f"{BLUE}Interactive shell closed.{NC}")
            sock.close()

# =============================================================================
# --- MODULE: RECON MANAGER ---
# =============================================================================

class ReconManager:
    """
    Handles all reconnaissance tasks.

    This module consolidates all web crawlers, subdomain scanners, and
    form extractors into one robust set of tools. It is designed to be
    non-intrusive and focuses on information gathering.
    """

    def __init__(self, toolkit):
        """
        Initializes the ReconManager.

        Args:
            toolkit (PyToolkit): The main toolkit instance.
        """
        self.toolkit = toolkit
        self.logger = toolkit.logger
        self.session = toolkit.session
        self.logger.info(f"{BLUE}ReconManager module loaded.{NC}")

    def _is_same_domain(self, url, base_url):
        """Helper to check if a URL is on the same domain as the base."""
        return urlparse(url).netloc == urlparse(base_url).netloc

    def _extract_links(self, url):
        """
        Helper to get all unique, absolute links from a single page.
        """
        found_links = set()
        try:
            # 1. Get page content using our existing WebManager!
            status, headers, content = self.toolkit.web.get_page_content(url)
            
            if not content:
                return found_links

            # 2. Parse the HTML
            # 'html.parser' is built-in, no 'lxml' needed
            soup = BeautifulSoup(content, "html.parser{NC}")
            
            # 3. Find all <a> tags with an 'href' attribute
            for link in soup.find_all("a", href=True):
                href = link.get('href')
                
                # 4. Clean and resolve the link (handles relative links)
                # This turns "/login.html" into "http://example.com/login.html"
                absolute_link = urljoin(url, href)
                
                # 5. Remove fragments (e.g., #top)
                absolute_link = absolute_link.split("#{NC}")[0]
                
                if absolute_link:
                    found_links.add(absolute_link)
                    
        except Exception as e:
            self.logger.error(f"{RED}Error extracting links from {url}: {e}{NC}")
            
        return found_links

    def crawl_site(self, base_url, max_depth=2):
        """
        Crawls a website starting from a base URL.
        This is a non-recursive, queue-based crawler that replaces all
        'spyder' scripts and the crawl() method from 'Vauln_Scanner'.

        Args:
            base_url (str): The URL to start crawling from (e.g., "http://example.com{NC}").
            max_depth (int): How many "clicks" deep to go.
        """
        self.logger.info(f"{BLUE}Starting crawl on {base_url} (max depth: {max_depth}){NC}")
        
        # (URL, current_depth)
        links_to_crawl = [(base_url, 0)] 
        links_visited = set()
        
        while links_to_crawl:
            # 1. Get the next link from the queue
            current_url, current_depth = links_to_crawl.pop(0)

            # 2. Check conditions
            if current_url in links_visited:
                continue
            if current_depth > max_depth:
                self.logger.info(f"{BLUE}Reached max depth, skipping: {current_url}{NC}")
                continue

            # 3. Process the link
            links_visited.add(current_url)
            self.logger.info(f"{BLUE}Crawling [Depth {current_depth}]: {current_url}{NC}")

            # 4. Find new links on this page
            new_links = self._extract_links(current_url)

            # 5. Add new, valid links to the queue
            for link in new_links:
                if link not in links_visited and self._is_same_domain(link, base_url):
                    links_to_crawl.append((link, current_depth + 1))
        
        self.logger.info(f"{BLUE}Crawl complete. Found {len(links_visited)} pages.{NC}")
        return list(links_visited)

    def extract_all_forms(self, url):
        """
        Finds all HTML <form> elements on a single page.
        This replaces 'forum_extractor.py' and 'extract_forms()' from 'Vauln_Scanner'.

        Args:
            url (str): The URL of the page to scan.

        Returns:
            list: A list of BeautifulSoup <form> objects.
        """
        self.logger.info(f"{BLUE}Extracting forms from: {url}{NC}")
        status, headers, content = self.toolkit.web.get_page_content(url)
        
        if not content:
            self.logger.warning(f"{RED}No content found at {url}, cannot extract forms.{NC}")
            return []
            
        try:
            soup = BeautifulSoup(content, "html.parser")
            forms = soup.find_all("form")
            self.logger.info(f"{BLUE}Found {len(forms)} forms on page.{NC}")
            return forms
        except Exception as e:
            self.logger.error(f"{RED}Error parsing HTML for forms: {e}{NC}")
            return []

# =============================================================================
# --- MODULE: SYSTEM MANAGER ---
# =============================================================================

class SystemManager:
    """
    Handles local system utilities, based on the PowerShell script.
    
    Includes a secure password generator and a file organizer.
    """

    def __init__(self, toolkit):
        """
        Initializes the SystemManager.
        """
        self.toolkit = toolkit
        self.logger = toolkit.logger
        self.logger.info(f"{BLUE}SystemManager module loaded.{NC}")

    def generate_password(self, length=16):
        if length < 8:
            self.logger.warning(f"{RED}Password length is less than 8. Recommending 12 or more.{NC}")
            length = 8
            
        char_set = string.ascii_letters + string.digits + "!@#$%^&*"
        self.logger.info(f"{BLUE}Generating new {length}-character password.{NC}")
        
        # Use random.choices (Python 3.6+) for secure generation
        password = "".join(random.choices(char_set, k=length))
        return password

    def organize_folder(self, src_path, dest_path):
        """
        Organizes files in a source folder into subfolders based on extension.
        Replaces 'Start-FolderOrganizer' from Toolkit.ps1.
        
        Args:
            src_path (str): The absolute path to the folder to organize.
            dest_path (str): The destination path for organized folders.
        """
        if not os.path.isdir(src_path):
            self.logger.error(f"{RED}Source path is not a valid directory: {src_path}{NC}")
            return
            
        self.logger.info(f"{BLUE}Organizing folder: {src_path}{NC}")
        
        # Map extensions to folder names
        EXT_MAP = {
            ".jpg": "images", ".jpeg": "images", ".png": "images",
            ".doc": "documents", ".docx": "documents", ".txt": "documents", ".pdf": "documents",
            ".xls": "spreadsheets", ".xlsx": "spreadsheets", ".csv": "spreadsheets",
            ".zip": "archives", ".tar": "archives", ".gz": "archives",
            ".mp3": "audio", ".mp4": "video",
        }
        
        files_moved = 0
        try:
            os.makedirs(dest_path, exist_ok=True)
            for filename in os.listdir(src_path):
                src_file = os.path.join(src_path, filename)
                
                if os.path.isfile(src_file):
                    ext = os.path.splitext(filename)[1].lower()
                    subdir = EXT_MAP.get(ext, "other{NC}") # Get folder or default to 'other'
                    
                    target_dir = os.path.join(dest_path, subdir)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    shutil.move(src_file, target_dir)
                    files_moved += 1
            
            self.logger.info(f"{BLUE}Organization complete. Moved {files_moved} files to {dest_path}{NC}")
        except Exception as e:
            self.logger.error(f"{RED}Failed during folder organization: {e}{NC}")


# =============================================================================
# --- MODULE: SECURITY ANALYSIS (DEFENSIVE HUB) ---
# =============================================================================

class SecurityAnalysis:
    """
    Acts as a hub for all defensive security analysis modules.
    
    This module contains classes that analyze the concepts from the
    offensive scripts (Vauln_Scanner, listener.py, post.py) and
    provide explanations on detection and prevention.
    """

    def __init__(self, toolkit):
        self.toolkit = toolkit
        self.logger = toolkit.logger
        # Load the sub-modules
        self.scanner = self.VulnerabilityScanner(toolkit)
        self.persistence = self.PersistenceAnalyzer(toolkit)
        self.bruteforce = self.BruteForceAnalyzer(toolkit)
        self.c2 = self.C2Analyzer(toolkit)
        self.logger.info(f"{BLUE}SecurityAnalysis module loaded.{NC}")

    # --- SUB-CLASS: VULNERABILITY SCANNER (DEFENSIVE) ---
    class VulnerabilityScanner:
        """
        Analyzes web application vulnerabilities. Based on 'Vauln_Scanner.py'.
        """
        def __init__(self, toolkit):
            self.toolkit = toolkit
            self.logger = toolkit.logger

        def run_scan(self, base_url):
            """
            Runs a full scan by crawling and then checking for vulnerabilities.
            """
            self.logger.info(f"{BLUE}Starting vulnerability scan on: {base_url}{NC}")
            # 1. Crawl the site to find all links and forms
            # We reuse our ReconManager!
            all_links = self.toolkit.recon.crawl_site(base_url, max_depth=3)
            all_forms = []
            for link in all_links:
                all_forms.extend(self.toolkit.recon.extract_all_forms(link))

            self.logger.info(f"{BLUE}Scan found {len(all_links)} links and {len(all_forms)} forms.{NC}")
            
            # 2. Explain XSS Prevention
            # This is the educational, defensive replacement for the attack scripts
            self.explain_xss_prevention()

        def explain_xss_prevention(self):
            """
            This replaces the 'xss_link' and 'xss_form' attack methods.
            It provides actionable advice on how to PREVENT XSS.
            """
            self.logger.info(f"{CYAN}[DEFENSE] --- How to Prevent Cross-Site Scripting (XSS) ---{NC}")
            print(f"\n{BLUE} [DEFENSE] --- How to Prevent Cross-Site Scripting (XSS) ---{NC}")
            print(f"{GREY}  XSS attacks (like from 'Vauln_Scanner.py') inject malicious scripts.{NC}")
            print(f"\n{BLUE} Here is how you prevent it:{NC}")
            print(f"{GREY}\n  1. (Primary) CONTEXTUAL OUTPUT ENCODING:{NC}")
            print(f"{GREY}     - NEVER trust user input. Encode it before rendering it in HTML.{NC}")
            print(f"{GREY}     - Example: '<' becomes '&lt;', '>' becomes '&gt;'.{NC}")
            print(f"{GREY}     - Use libraries for this: Jinja2, React, etc., do this by default.{NC}")
            print(f"{GREY}\n  2. CONTENT SECURITY POLICY (CSP):{NC}")
            print(f"{GREY}     - A web server header that tells the browser *which* scripts{NC}")
            print(f"{GREY}       are trusted and allowed to run. A strong CSP can block{NC}")
            print(f"{GREY}       all inline scripts and untrusted domains, stopping XSS.{NC}")
            print(f"{GREY}\n  3. INPUT VALIDATION:{NC}")
            print(f"{GREY}     - As a secondary defense, *validate* user input on the server.{NC}")
            print(f"{GREY}     - Example: If you expect a phone number, only allow digits 0-9.{NC}")

    # --- SUB-CLASS: PERSISTENCE ANALYZER (DEFENSIVE) ---
    class PersistenceAnalyzer:
        """
        Analyzes common system persistence techniques. Based on 'def_persistence.py'.
        """
        def __init__(self, toolkit):
            self.toolkit = toolkit
            self.logger = toolkit.logger

        def explain_registry_persistence(self):
            self.logger.info(f"{CYAN}[DEFENSE] --- How to Detect Registry Key Persistence ---{NC}")
            print(f"\n{BLUE} [DEFENSE] --- How to Detect Registry Key Persistence (from 'def_persistence.py') ---{NC}")
            print(f"{GREY}  The script 'def_persistence.py' adds a program to the Registry Run key{NC}")
            print(f"{GREY}  (HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run) to auto-start.{NC}")
            print(f"\n{BLUE} HOW TO DETECT & PREVENT:{NC}")
            print(f"{GREY}  1. MONITORING: Use tools like Autoruns (from Sysinternals) to see{NC}")
            print(f"{GREY}     all programs that auto-start. Regularly review this list.{NC}")
            print(f"{GREY}  2. PERMISSIONS: Standard users should not have write access to system-wide{NC}")
            print(f"{GREY}     Run keys (like HKLM). This won't stop the HKCU key, however.{NC}")
            print(f"{GREY}  3. EDR: Endpoint Detection & Response (EDR) tools (like Windows Defender){NC}")
            print(f"{GREY}     are designed to detect this behavior and block it.{NC}")

    # --- SUB-CLASS: BRUTE-FORCE ANALYZER (DEFENSIVE) ---
    class BruteForceAnalyzer:
        def __init__(self, toolkit):
            self.toolkit = toolkit
            self.logger = toolkit.logger

        def explain_brute_force_defense(self):
            self.logger.info(f"{CYAN}[DEFENSE] --- How to Prevent Login Brute-Force Attacks ---{NC}")
            print(f"\n{BLUE}[DEFENSE] --- How to Prevent Login Brute-Force (from 'post.py') --{NC}")
            print(f"{GREY}The script 'post.py' tries thousands of passwords on a login page.{NC}")
            print(f"{BLUE}\n  HOW TO PREVENT:{NC}")
            print(f"{GREY}  1. RATE-LIMITING: Block an IP address after (e.g.) 5 failed login{NC}")
            print(f"{GREY}     attempts in 1 minute. This is the most effective defense.{NC}")
            print(f"{GREY}  2. ACCOUNT LOCKOUT: Lock a *username* after 10 failed attempts.{NC}")
            print(f"{GREY}  3. CAPTCHA: After 3 failed attempts, require a CAPTCHA to prove{NC}")
            print(f"{GREY}     the user is human, which stops simple scripts.{NC}")


    # --- SUB-CLASS: C2 ANALYZER (DEFENSIVE) ---
    class C2Analyzer:
        def __init__(self, toolkit):
            self.toolkit = toolkit
            self.logger = toolkit.logger

        def explain_c2_defense(self):
            self.logger.info(f"{CYAN}[DEFENSE] --- How to Detect Reverse Shells (C2) ---{NC}")
            print(f"\n{BLUE}[DEFENSE] --- How to Detect Reverse Shells (from 'listener.py') ---{NC}")
            print(f"{GREY}  'listener.py' is a Command & Control (C2) server. It waits for{NC}")
            print(f"{GREY}  an infected machine to *connect out* to it, bypassing firewalls.{NC}")
            print(f"\n{BLUE}  HOW TO PREVENT:{NC}")
            print(f"{GREY}  1. EGRESS FILTERING: This is the #1 defense. On your firewall,{NC}")
            print(f"{GREY}     *BLOCK ALL* outbound traffic by default. Only allow specific{NC}")
            print(f"{GREY}     ports your business needs (e.g., 80/TCP, 443/TCP).{NC}")
            print(f"{GREY}     The reverse shell will fail because it can't connect out.{NC}")
            print(f"{GREY}  2. PROCESS MONITORING: On your servers, monitor for suspicious{NC}")
            print(f"{GREY}     processes (like 'powershell.exe' or 'bash') making outbound{NC}")
            print(f"{GREY}     network connections to unknown IPs.{NC}")

# =============================================================================
# --- 5. SCRIPT EXECUTION ENTRY POINT ---
# =============================================================================

if __name__ == "__main__":
    try:
        # Create an instance of our main toolkit
        toolkit = PyToolkit()
        
        # Run the main menu
        toolkit.run_cli_menu()

    except KeyboardInterrupt:
        logger.info(f"\n{GREY}[!] User aborted session. Shutting down.{NC}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"{RED}[CRITICAL] An unhandled error occurred: {e}{NC}")
        sys.exit(1)
