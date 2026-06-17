import os
import requests
from bs4 import BeautifulSoup
import shutil

class AutoWebCloner:
    def __init__(self, target_url, data_folder, output_folder):
        self.target_url = target_url
        self.data_folder = data_folder
        self.output_folder = output_folder
        self.customer_texts = []
        self.customer_images = []

    def scan_customer_data(self):
        print(f"[*] Scanning customer data in {self.data_folder}...")
        
        # Scan Text files
        if os.path.exists(self.data_folder):
            for filename in os.listdir(self.data_folder):
                if filename.endswith(".txt"):
                    filepath = os.path.join(self.data_folder, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().split('\n')
                        # filter empty lines
                        content = [c.strip() for c in content if c.strip()]
                        self.customer_texts.extend(content)
                        
        # Scan Images
        img_dir = os.path.join(self.data_folder, "images")
        if os.path.exists(img_dir):
            for filename in os.listdir(img_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                    self.customer_images.append(filename)
                    
        print(f"[+] Found {len(self.customer_texts)} text blocks and {len(self.customer_images)} images.")

    def clone_website(self):
        print(f"[*] Cloning website layout from: {self.target_url}...")
        try:
            # We add headers to simulate a real browser
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
            response = requests.get(self.target_url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[-] Failed to clone website: {e}")
            return None

    def inject_data(self, html_content):
        print("[*] Injecting customer data into the cloned layout...")
        soup = BeautifulSoup(html_content, 'html.parser')

        # Replace Text (Headings and Paragraphs)
        text_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'span', 'a'])
        text_idx = 0
        for tag in text_tags:
            # Only replace if the tag has some visible text, is not empty, and has no nested critical tags
            if tag.string and tag.string.strip() and text_idx < len(self.customer_texts):
                tag.string.replace_with(self.customer_texts[text_idx])
                text_idx += 1

        # Replace Images
        img_tags = soup.find_all('img')
        img_idx = 0
        for img in img_tags:
            if img_idx < len(self.customer_images):
                new_src = "images/" + self.customer_images[img_idx]
                img['src'] = new_src
                img_idx += 1

        print(f"[+] Replaced {text_idx} text elements and {img_idx} image elements.")
        
        # Inject a base tag to fix relative links from the original site (optional but good for CSS/JS)
        if soup.head:
            base_tag = soup.new_tag("base", href=self.target_url if self.target_url.endswith('/') else self.target_url + '/')
            soup.head.insert(0, base_tag)
            
        return str(soup)

    def generate_output(self, final_html):
        print(f"[*] Saving final website to {self.output_folder}...")
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Write HTML
        index_path = os.path.join(self.output_folder, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        # Copy images to output
        out_img_dir = os.path.join(self.output_folder, "images")
        os.makedirs(out_img_dir, exist_ok=True)
        
        src_img_dir = os.path.join(self.data_folder, "images")
        if os.path.exists(src_img_dir):
            for img_name in self.customer_images:
                shutil.copy(os.path.join(src_img_dir, img_name), os.path.join(out_img_dir, img_name))

        print(f"[+] Website successfully generated at: {os.path.abspath(index_path)}")

    def run(self):
        self.scan_customer_data()
        if not self.customer_texts and not self.customer_images:
            print("[-] No customer data found! Please add .txt files or images to the customer_data folder.")
            return

        html = self.clone_website()
        if html:
            final_html = self.inject_data(html)
            self.generate_output(final_html)
            print("[✓] Process Complete!")

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("="*50)
    print("   [+] Auto Website Cloner & Injector")
    print("="*50)
    
    target_url = input("Enter Target URL to Clone (e.g. https://example.com): ")
    
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer_data")
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_website")
    
    cloner = AutoWebCloner(target_url, data_folder, output_folder)
    cloner.run()
