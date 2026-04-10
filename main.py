import os
import sys
import requests
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Unique User-Agent
HEADERS = {'User-Agent': 'python:reddit_media_scraper:v6.4 (by /u/Akshay_Dev_Project)'}

def load_list_from_file(filepath):
    if not filepath or not os.path.exists(filepath): return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

def safe_get(url, params=None, retries=3):
    if not url: return None
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if response.status_code == 429:
                time.sleep((i + 1) * 10); continue
            response.raise_for_status()
            return response
        except:
            if i == retries - 1: return None
            time.sleep(2)
    return None

def extract_links_categorized(data):
    images, videos = set(), set()
    img_exts = ['.jpg', '.jpeg', '.png', '.webp']
    vid_exts = ['.mp4', '.webm', '.mov', '.gif', '.gifv']
    
    children = data.get('data', {}).get('children', [])
    for child in children:
        post = child.get('data', {})
        url = post.get('url', '')
        if any(ext in url.lower() for ext in img_exts):
            images.add(url.split('?')[0].replace('&amp;', '&'))
        elif any(ext in url.lower() for ext in vid_exts):
            videos.add(url.replace('&amp;', '&'))

        sources = [post]
        if post.get('crosspost_parent_list'): sources.extend(post['crosspost_parent_list'])
        for s in sources:
            m = s.get('media') or s.get('secure_media')
            if m and m.get('reddit_video'):
                v = m['reddit_video'].get('fallback_url')
                if v: videos.add(v.replace('&amp;', '&'))
            p = s.get('preview', {})
            if p.get('reddit_video_preview'):
                v = p['reddit_video_preview'].get('fallback_url')
                if v: videos.add(v.replace('&amp;', '&'))

        meta = post.get('media_metadata')
        if meta:
            for item_id in meta:
                item = meta[item_id]
                if isinstance(item, dict) and item.get('s'):
                    g_url = item['s'].get('u') or item['s'].get('gif')
                    if g_url:
                        if '.gif' in g_url.lower(): videos.add(g_url.replace('&amp;', '&'))
                        else: images.add(g_url.replace('&amp;', '&'))
    return images, videos

def download_file(link, base_dl_path):
    try:
        filename = link.split('/')[-1].split('?')[0]
        ext = os.path.splitext(filename)[1].lower()
        if "DASH_" in filename and not ext: filename += ".mp4"; ext = ".mp4"
        
        v_exts = ['.mp4', '.webm', '.mov', '.gif', '.gifv']
        target_dir = os.path.join(base_dl_path, "videos") if (ext in v_exts or 'video' in link.lower()) else base_dl_path
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)

        if os.path.exists(filepath): return 0
        res = safe_get(link)
        if res and res.status_code == 200:
            with open(filepath, 'wb') as f: f.write(res.content)
            return 1
        return -1
    except: return -1

def run_scraper(name, source_type, max_workers, base_output, v_on, ask=False, gui_cb=None):
    sub = f"r_{name}" if source_type == "subreddit" else name
    path = os.path.join(base_output, sub, 'downloads')
    os.makedirs(path, exist_ok=True)

    all_i, all_v = set(), set()
    after = None
    url = f"https://www.reddit.com/user/{name}/submitted.json" if source_type == "user" else f"https://www.reddit.com/r/{name}/hot.json"
    
    if gui_cb: gui_cb(name, "Scanning...", "...")
    while True:
        res = safe_get(url, params={'limit': 100, 'after': after})
        if not res: break
        data = res.json()
        i, v = extract_links_categorized(data)
        all_i.update(i); all_v.update(v)
        if gui_cb: gui_cb(name, len(all_i), len(all_v))
        after = data.get('data', {}).get('after')
        if not after: break
        time.sleep(1.2)

    f_list = []
    if ask:
        print(f"\n--- TARGET: {name} ---")
        print(f"Images: {len(all_i)} | Videos: {len(all_v)}")
        if v_on:
            print("1. All | 2. Images | 3. Videos | 4. Skip")
            c = input("Choice (1-4): ").strip()
        else:
            print("1. Images | 2. Skip")
            c = input("Choice (1-2): ").strip()
            
        if c == '1': f_list = list(all_i | all_v) if v_on else list(all_i)
        elif c == '2' and v_on: f_list = list(all_i)
        elif c == '3' and v_on: f_list = list(all_v)
        else: return
    else:
        f_list = list(all_i | all_v) if v_on else list(all_i)

    if f_list:
        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            futures = {exe.submit(download_file, u, path): u for u in f_list}
            with tqdm(total=len(f_list), unit="file", desc=f"    {name[:10]}", dynamic_ncols=True) as pbar:
                for future in as_completed(futures):
                    pbar.update(1)

# --- GUI ---
class ScraperGUI:
    def __init__(self, root):
        self.root = root; self.root.title("Reddit Scraper v6.4"); self.root.geometry("850x700")
        self.root.configure(bg="#f0f0f0")
        
        f1 = tk.Frame(root, bg="#f0f0f0"); f1.pack(pady=10)
        tk.Label(f1, text="Username(s):", bg="#f0f0f0", font=('Arial', 11)).grid(row=0, column=0, sticky="e", padx=5)
        self.u_entry = tk.Entry(f1, width=80); self.u_entry.grid(row=0, column=1, pady=5)
        tk.Label(f1, text="Community(s):", bg="#f0f0f0", font=('Arial', 11)).grid(row=1, column=0, sticky="e", padx=5)
        self.r_entry = tk.Entry(f1, width=80); self.r_entry.grid(row=1, column=1, pady=5)

        tk.Label(root, text="-------------------------- List Selection --------------------------", bg="#f0f0f0", fg="#666").pack()
        f2 = tk.Frame(root, bg="#f0f0f0"); f2.pack(pady=10)
        tk.Button(f2, text="Browse User List", command=self.get_u_file, width=15).grid(row=0, column=0, padx=10)
        self.u_file_lbl = tk.Label(f2, text="{None}", fg="grey", bg="#f0f0f0"); self.u_file_lbl.grid(row=0, column=1, sticky="w")
        tk.Button(f2, text="Browse Sub List", command=self.get_r_file, width=15).grid(row=1, column=0, padx=10, pady=5)
        self.r_file_lbl = tk.Label(f2, text="{None}", fg="grey", bg="#f0f0f0"); self.r_file_lbl.grid(row=1, column=1, sticky="w")

        tk.Label(root, text="-------------------------- Video & Worker --------------------------", bg="#f0f0f0", fg="#666").pack()
        f3 = tk.Frame(root, bg="#f0f0f0"); f3.pack(pady=10)
        self.v_var = tk.BooleanVar(value=False); tk.Checkbutton(f3, text="Video :", variable=self.v_var, bg="#f0f0f0").grid(row=0, column=0)
        self.ask_var = tk.BooleanVar(value=False); tk.Checkbutton(f3, text="Ask :", variable=self.ask_var, bg="#f0f0f0").grid(row=0, column=1, padx=20)
        tk.Label(f3, text="Workers:", bg="#f0f0f0").grid(row=0, column=2); self.w_spin = tk.Spinbox(f3, from_=4, to=20, width=5); self.w_spin.grid(row=0, column=3)

        self.log = scrolledtext.ScrolledText(root, width=100, height=12); self.log.pack(padx=20, pady=5)
        self.btn = tk.Button(root, text="START SCRAPING", command=self.start, bg="#2c3e50", fg="white", width=25); self.btn.pack(pady=10)
        self.status = tk.Label(root, text="Ready", bg="#f0f0f0", font=('Arial', 10, 'bold')); self.status.pack(side="bottom", pady=15)
        self.u_path, self.r_path = None, None

    def get_u_file(self): self.u_path = filedialog.askopenfilename(); self.u_file_lbl.config(text=os.path.basename(self.u_path))
    def get_r_file(self): self.r_path = filedialog.askopenfilename(); self.r_file_lbl.config(text=os.path.basename(self.r_path))
    def update_status(self, name, i, v): self.status.config(text=f"Username : {name}   Images : {i}   Videos : {v}")
    def start(self): threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        targets = [(u, "user") for u in self.u_entry.get().split()]
        targets += [(r, "subreddit") for r in self.r_entry.get().split()]
        if self.u_path: targets += [(u, "user") for u in load_list_from_file(self.u_path)]
        if self.r_path: targets += [(r, "subreddit") for r in load_list_from_file(self.r_path)]
        
        seen = set()
        for name, stype in [x for x in targets if not (x in seen or seen.add(x))]:
            run_scraper(name, stype, int(self.w_spin.get()), os.getcwd(), self.v_var.get(), self.ask_var.get(), self.update_status)
        messagebox.showinfo("Done", "Complete!")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-gui", action="store_true")
    p.add_argument("-u", "--username", nargs='+')
    p.add_argument("-r", "--community", nargs='+')
    p.add_argument("-listu", "--userlist")
    p.add_argument("-listr", "--communitylist")
    p.add_argument("-w", "--workers", type=int, default=4)
    p.add_argument("-o", "--output", default=".")
    p.add_argument("-c", "--cooldown", type=int, default=0)
    p.add_argument("-v", "--video", choices=['y', 'n'], default='n')
    p.add_argument("-ask", action="store_true")
    args = p.parse_args()

    # RESTORED LOGIC: Only launch GUI if requested
    if args.gui:
        root = tk.Tk(); app = ScraperGUI(root); root.mainloop()
        sys.exit()

    # Check for CLI targets
    targets = []
    if args.username: [targets.append((u, "user")) for u in args.username]
    if args.userlist: [targets.append((u, "user")) for u in load_list_from_file(args.userlist)]
    if args.community: [targets.append((c, "subreddit")) for c in args.community]
    if args.communitylist: [targets.append((c, "subreddit")) for c in load_list_from_file(args.communitylist)]

    if not targets:
        # If no CLI targets AND no GUI flag, enter Interactive Text mode
        print("=== INTERACTIVE MODE ===")
        u_in = input("Usernames (space separated): ")
        r_in = input("Communities (space separated): ")
        if not u_in and not r_in:
            print("No targets. Launching GUI instead..."); root = tk.Tk(); app = ScraperGUI(root); root.mainloop(); sys.exit()
        
        targets += [(u, "user") for u in u_in.split()]
        targets += [(r, "subreddit") for r in r_in.split()]
        args.video = input("Download videos? (y/n): ") or 'n'
        args.ask = (input("Use Ask mode? (y/n): ") == 'y')

    # Execute CLI/Interactive
    out = os.path.expanduser(args.output)
    v_on = (args.video == 'y')
    seen = set()
    final_targets = [x for x in targets if not (x in seen or seen.add(x))]

    for i, (name, stype) in enumerate(final_targets):
        run_scraper(name, stype, args.workers, out, v_on, args.ask)
        if args.cooldown > 0 and i < len(final_targets) - 1:
            time.sleep(args.cooldown)
