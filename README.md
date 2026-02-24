# IU Course Catalog Automation and Data Scraping Tool

A high-performance web automation script built with **Python** and **Playwright** designed to extract real-time academic data from the Indiana University (IGPS) portal. This tool navigates complex asynchronous interfaces to deliver structured insights into course availability, instructor assignments, and section-specific metadata.
## Project Demo
https://github.com/user-attachments/assets/16153a28-e928-4b54-8e73-1b257a145b80


## 🚀 Key Features

* **Dynamic SPA Navigation:** Orchestrates multi-campus and multi-term searches across highly reactive, JavaScript-heavy interfaces.
* **Adaptive Extraction Logic:** Automatically detects and parses data from two distinct UI architectures:
    * *Standard Layout:* Single-component table structures.
    * *Multi-Component Layout:* Complex nested rows for courses requiring linked Lectures, Labs, and Discussions.
* **Automated Data Flattening:** Efficiently maps hierarchical web data (Course > Sections > Instructors) into a normalized **CSV format** optimized for data analysis and BI tools.
* **Resilient Automation:** Utilizes event-driven "wait states" and state-aware locators to eliminate race conditions, ensuring stability during modal transitions and layout shifts.

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Automation Framework:** Playwright (Chromium)
* **Data Processing:** CSV, JSON
* **Architecture:** Procedural Automation with Error Handling

## 📊 Data Points Extracted

| Field | Description |
| :--- | :--- |
| **Campus & Subject** | Geographic and departmental classification. |
| **Course Metadata** | Unique ID, Title, and Credit hours. |
| **Section Type** | Categorization of Lecture, Lab, or Discussion components. |
| **Instructor** | Full names of all assigned faculty (supports multi-instructor rows). |
| **Availability** | Real-time "Open Seats" ratio and Waitlist status. |

## ⚙️ Setup & Usage

1. **Clone the repository and install dependencies:**
   ```bash
   pip install playwright
   playwright install chromium

2. **Execute the enginer**
```python scraper.py```

## Technical Challenges Overcome**
The IU IGPS portal presents several hurdles for standard scrapers, including:

Race Conditions: Solved by implementing wait_for_selector logic to sync the scraper with the portal's asynchronous data loading.

DOM Variation: Engineered a unified extraction logic that handles both rvt-m-bottom-sm tables and rvt-border-top multi-component lists using relative XPath and CSS selectors.

Memory Management: Implemented real-time file-append logic to ensure data persistence and low memory overhead during large-scale campus-wide scrapes.
