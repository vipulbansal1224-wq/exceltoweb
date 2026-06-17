# Auto Web Cloner

Clone any website's design and automatically inject your customer's data into it.

## Features
- Clone any website layout (HTML/CSS)
- Inject customer text (.txt) and images automatically
- Download the complete generated website as a ZIP file
- Web UI built with Flask

## How to Use

### 1. Install dependencies
```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### 2. Add customer data
Put customer `.txt` files and images in the `customer_data/` folder:
```
customer_data/
  about_us.txt
  services.txt
  images/
    logo.png
    banner.jpg
```

### 3. Run Web UI
```bash
.\venv\Scripts\python.exe web_app.py
```
Open: http://127.0.0.1:8080

### 4. Or use Command Line
```bash
.\venv\Scripts\python.exe main.py
```

## Output
Generated website saved to `output_website/` folder and downloadable as `cloned_website.zip`.
