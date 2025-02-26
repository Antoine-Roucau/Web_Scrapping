import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd
from typing import List, Dict, Set
import re

# Class for the write-up crawler
class WriteupCrawler:
    def __init__(self, base_url: str = "https://writeups.ayweth20.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.visited_urls: Set[str] = set()
        
    # Method to get the content of a page
    def get_page_content(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error retrieving {url}: {e}")
            return None

    # Method to check if a URL is a write-up
    def is_writeup_url(self, url: str) -> bool:
        pattern = r"/\d{4}/(?:dvctf|404ctf|operation-kernel)[-\w]*/.+?"
        return bool(re.search(pattern, url))

    # Method to collect write-up URLs
    def collect_writeup_urls(self, start_urls: List[str]) -> List[str]:
        writeup_urls = set()
        urls_to_visit = set(start_urls)
        
        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in self.visited_urls:
                continue
                
            print(f"Exploring: {current_url}")
            self.visited_urls.add(current_url)
            
            soup = self.get_page_content(current_url)
            if not soup:
                continue
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                if not full_url.startswith(self.base_url):
                    continue
                    
                if self.is_writeup_url(full_url):
                    writeup_urls.add(full_url)
                    print(f"Write-up found: {full_url}")
                elif full_url not in self.visited_urls and any(ctf_url in full_url for ctf_url in start_urls):
                    urls_to_visit.add(full_url)
        
        return list(writeup_urls)

    # Method to parse a write-up URL
    def parse_writeup_url(self, url: str) -> Dict:
        path_segments = urlparse(url).path.strip('/').split('/')
        
        try:
            year = path_segments[0]
            
            if "dvctf-to-join-davincicode" in url:
                ctf = "DVCTF"
                category = path_segments[-2] if len(path_segments) > 2 else "N/A"
                title = path_segments[-1]
            elif "404ctf" in url:
                ctf = "404 CTF"
                category = path_segments[-2]
                title = path_segments[-1]
            elif "operation-kernel" in url:
                ctf = "Operation Kernel"
                category = path_segments[-2]
                title = path_segments[-1]
            else:
                ctf = path_segments[1]
                category = path_segments[-2] if len(path_segments) > 2 else "N/A"
                title = path_segments[-1]
            
            return {
                'Year': year,
                'CTF': ctf,
                'Category': category,
                'Title': title.replace('-', ' ').title(),
                'URL': url
            }
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            
        return {
            'Year': 'N/A',
            'CTF': 'N/A',
            'Category': 'N/A',
            'Title': 'N/A',
            'URL': url
        }

# Main function
def main():
    ctf_urls = [
        "https://writeups.ayweth20.com/2021/dvctf-to-join-davincicode",
        "https://writeups.ayweth20.com/2022/dvctf-2022",
        "https://writeups.ayweth20.com/2022/404ctf",
        "https://writeups.ayweth20.com/2022/operation-kernel",
        "https://writeups.ayweth20.com/2023/404ctf-2023"
    ]
    
    crawler = WriteupCrawler()
    
    print("Collecting write-up URLs...")
    writeup_urls = crawler.collect_writeup_urls(ctf_urls)
    print(f"\nNumber of write-ups found: {len(writeup_urls)}")
    
    print("\nAnalyzing write-ups...")
    writeups_data = []
    for url in writeup_urls:
        writeups_data.append(crawler.parse_writeup_url(url))
    
    df = pd.DataFrame(writeups_data)
    
    df = df.sort_values(['Year', 'CTF', 'Category', 'Title'])
    
    output_file = 'ctf_collection.xlsx'
    print(f"\nSaving data to {output_file}...")
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Writeups', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Writeups']
        
        # Formatting the header
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        for idx, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).apply(len).max(), len(col))
            worksheet.set_column(idx, idx, max_length + 2)
    
    print("Done!")
    print(f"\nPreview of collected data ({len(writeups_data)} write-ups):")
    print(df.head())
    
    print("\nSummary by CTF:")
    print(df.groupby(['Year', 'CTF']).size())

if __name__ == "__main__":
    main()