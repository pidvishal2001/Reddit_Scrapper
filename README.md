# 🚀 Reddit Scrapper

A powerful **multi-threaded Reddit media scraper** built in Python that allows you to download images and videos from Reddit **users** and **subreddits** — with support for CLI, GUI, and interactive modes.

---

## ✨ Features

* 📥 Download media from:

  * Reddit users (`/user/...`)
  * Subreddits (`/r/...`)
* 🖼️ Automatically detects:

  * Images (`.jpg`, `.png`, `.webp`, etc.)
  * Videos (`.mp4`, `.gif`, `.webm`, etc.)
* ⚡ Multi-threaded downloads (faster scraping)
* 🧠 Smart retry system (handles rate limits & errors)
* 🖥️ GUI support (Tkinter-based)
* 💻 CLI + Interactive mode support
* 📂 Organized output (separates videos & images)
* 📃 Supports list input from files

---

## 🛠️ Tech Stack

* Python 3
* `requests`
* `tqdm`
* `tkinter`
* `concurrent.futures`

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/pidvishal2001/Reddit_Scrapper.git
cd reddit-scrapper
```

Install dependencies:

```bash
pip install requests tqdm
```

> ⚠️ `tkinter` usually comes pre-installed with Python.

---

## 🚀 Usage

### 🔹 1. CLI Mode

Download from a user:

```bash
python script.py -u username
```

Download from a subreddit:

```bash
python script.py -r memes
```

Download both:

```bash
python script.py -u username -r memes
```

---

### 🔹 2. With Options

| Option   | Description                 |
| -------- | --------------------------- |
| `-w`     | Number of workers (threads) |
| `-o`     | Output directory            |
| `-v y/n` | Download videos             |
| `-ask`   | Ask before downloading      |
| `-listu` | File with usernames         |
| `-listr` | File with subreddits        |

Example:

```bash
python script.py -u username -w 10 -v y -o downloads
```
```bash
python script.py \
-u username1 username2 \
-r memes funny \
-listu user_list.txt \
-listr subreddit_list.txt \
-w 10 \
-o ./downloads \
-c 2 \
-v y \
-ask
```
🔍 Explanation
-u → List of usernames
-r → List of subreddits
-listu → File containing usernames
-listr → File containing subreddits
-w → Number of worker threads
-o → Output directory
-c → Cooldown (seconds between targets)
-v y/n → Enable/disable video download
-ask → Ask before downloading media
---

### 🔹 3. GUI Mode

Launch GUI:

```bash
python script.py -gui
```

Features:

* Enter usernames & subreddits
* Load list files
* Toggle video download
* Set workers
* Live status updates

---

### 🔹 4. Interactive Mode

Just run:

```bash
python script.py
```

Then follow prompts:

* Enter usernames
* Enter subreddits
* Choose video download
* Enable ask mode

---

## 📁 Output Structure

```
output/
 ├── username/
 │    └── downloads/
 │         ├── image1.jpg
 │         ├── image2.png
 │         └── videos/
 │              ├── video1.mp4
 │              └── video2.webm
```

---

## 🧠 How It Works

1. Fetches Reddit JSON data (`hot.json` / `submitted.json`)
2. Extracts:

   * Direct media links
   * Reddit hosted videos
   * Crossposts & previews
3. Categorizes into images/videos
4. Downloads using multi-threading

---

## ⚠️ Notes

* Uses Reddit public endpoints (no API key required)
* May hit rate limits (handled automatically with retries)
* Respect Reddit's terms of service

---

## 🧩 Future Improvements

* Resume downloads
* Proxy support
* Better filtering (by date, upvotes, etc.)
* GUI enhancements

---

## 👨‍💻 Author

Developed by **Akshay Dev Project**

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🍴 Fork it
* 🧠 Contribute improvements

---

## 📜 License

This project is open-source and free to use.

---
