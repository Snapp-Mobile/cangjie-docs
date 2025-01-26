import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# Step 1: Base URL and Starting Page
base_url = "https://docs.cangjie-lang.cn"
start_url = f"{base_url}/docs/0.53.13/user_manual/source_zh_cn/first_understanding/basic.html"
headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a browser

# Output Directories
output_dir = "scraped_site"
css_dir = os.path.join(output_dir, "css")
js_dir = os.path.join(output_dir, "js")
os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

# Function to download a resource and save it locally
def download_resource(url, output_folder):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Extract the filename from the URL
            file_name = os.path.basename(urlparse(url).path)
            file_path = os.path.join(output_folder, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            print(f"Failed to download resource: {url}")
    except Exception as e:
        print(f"Error downloading resource {url}: {e}")
    return None

# Step 2: Fetch the Starting Page
response = requests.get(start_url, headers=headers)

# Fix the encoding issue
response.encoding = response.apparent_encoding  # Dynamically detect the correct encoding

if response.status_code != 200:
    print(f"Failed to fetch the starting page: {start_url}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Step 3: Extract Navigation Links from <nav id="sidebar">
nav = soup.find("nav", id="sidebar")
if not nav:
    print("Navigation sidebar not found!")
    exit()

# Resolve relative URLs to absolute URLs
links = [urljoin(start_url, a['href']) for a in nav.find_all("a", href=True)]

# Step 4: Limit to the First 4 Pages
links = links[:4]  # Only take the first 4 links for testing

# Step 5: Loop through links and save HTML, CSS, and JavaScript
for idx, link in enumerate(links, start=1):
    print(f"Scraping page {idx}/{len(links)}: {link}")
    
    page_response = requests.get(link, headers=headers)

    # Fix the encoding issue for each page
    page_response.encoding = page_response.apparent_encoding

    if page_response.status_code != 200:
        print(f"Failed to fetch the page: {link}")
        continue

    page_soup = BeautifulSoup(page_response.text, "html.parser")
    
    # Create the corresponding directory structure for the HTML file
    parsed_url = urlparse(link)
    relative_path = os.path.relpath(parsed_url.path, "/docs/0.53.13")  # Remove base structure
    html_file_path = os.path.join(output_dir, relative_path)
    os.makedirs(os.path.dirname(html_file_path), exist_ok=True)  # Create directories if necessary

    # Determine relative path from the HTML file to the root (for proper CSS/JS linking)
    relative_to_root = os.path.relpath(output_dir, os.path.dirname(html_file_path))
    
    # Download and replace CSS links
    for css_tag in page_soup.find_all("link", rel="stylesheet", href=True):
        css_url = urljoin(link, css_tag["href"])  # Resolve the CSS URL
        local_css_path = download_resource(css_url, css_dir)
        if local_css_path:
            # Update href to the relative path from the HTML file to the local CSS file
            css_tag["href"] = os.path.join(relative_to_root, "css", os.path.basename(local_css_path)).replace("\\", "/")

    # Download and replace JS links
    for js_tag in page_soup.find_all("script", src=True):
        js_url = urljoin(link, js_tag["src"])  # Resolve the JS URL
        local_js_path = download_resource(js_url, js_dir)
        if local_js_path:
            # Update src to the relative path from the HTML file to the local JS file
            js_tag["src"] = os.path.join(relative_to_root, "js", os.path.basename(local_js_path)).replace("\\", "/")

    # Save the modified HTML
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(page_soup.prettify())
    
    print(f"Saved HTML: {html_file_path}")

print("\nScraping complete! Check the 'scraped_site' folder.")

