
# Multi-Source News Aggregator Application

A Python-based Command-Line Interface (CLI) application designed to collect, parse, and centralize real-time news updates from multiple concurrent streams. The application seamlessly integrates **NewsAPI (JSON/REST)** and public **RSS Feeds (XML)** into a single, de-duplicated terminal experience.

---

## 🚀 Features

- **Multi-Source Integration:** Fetches global headlines concurrently from NewsAPI and public BBC RSS feeds.
- **Content Filtering:** Supports keyword-based search and strict filtering across major categories (Technology, Sports, Business, Entertainment).
- **Data Deduplication:** Implements automated filtering mechanisms to eliminate redundant news entries sharing identical titles.
- **Persistence & Bookmarking:** Allows users to bookmark favorite articles into a JSON database and export localized feeds into structured CSV files for offline analysis.
- **Robust Error Handling:** Built-in safeguards against API request timeouts, server-side threshold limitations, and network connection drops.

---

## 🛠️ Tech Stack & Prerequisites

- **Language:** Python 3.8+
- **Libraries Used:** `requests`, `json`, `csv`, `os`, `xml.etree.ElementTree`

No heavy external dependencies are required beyond the standard library, except for the `requests` package.

---

## ⚙️ Installation & Local Setup

### 1. Project Initialization
Open your terminal,command prompt(CMD),or pycarm terminal directly inside your project folder.

### 2. Install Dependencies
Ensure you have the required Python HTTP library installed:

Bash
pip install requests

### 3. Generate an API Key
Visit NewsAPI.org and sign up for a free developer account.

Generate your unique API Key.

### 4. Environment Configuration
Create a configuration file named config.json in the root directory of the project. Do not commit this file to GitHub. Paste your API key using the following JSON schema:

JSON
{
  "api_key": "YOUR_ACTUAL_NEWSAPI_KEY"
}

🖥️ Usage
Execute the main script from your terminal to launch the application's interactive menu:

Bash
python Task 12 News aggregator.py

##**Demo Video**:
You can see working in:
News Aggregatorr demo video.mp4
