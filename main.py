from io import BytesIO
from pathlib import Path
import json
from datetime import datetime
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import requests
from PIL import Image, ImageTk
import yt_dlp
from yt_dlp.utils import sanitize_filename


BG_COLOR = "#F5F7FB"
CARD_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4F46E5"
ACCENT_HOVER = "#4338CA"
SUCCESS_COLOR = "#059669"
WARNING_COLOR = "#D97706"
ERROR_COLOR = "#DC2626"
TEXT_COLOR = "#111827"
SUBTEXT_COLOR = "#6B7280"
MUTED_COLOR = "#9CA3AF"
BORDER_COLOR = "#E5E7EB"
SOFT_BG = "#EEF2FF"

TITLE_FONT = ("Arial", 22, "bold")
SECTION_FONT = ("Arial", 10, "bold")
BODY_FONT = ("Arial", 10)
SMALL_FONT = ("Arial", 9)
BUTTON_FONT = ("Arial", 10, "bold")
INFO_TITLE_FONT = ("Arial", 13, "bold")
INFO_FONT = ("Arial", 10)


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("860x930")
        self.root.minsize(860, 930)
        self.root.resizable(True, True)
        self.root.configure(bg=BG_COLOR)

        self.url_var = tk.StringVar()
        self.download_folder = tk.StringVar()
        self.quality_var = tk.StringVar(value="Best quality")
        self.progress_var = tk.DoubleVar(value=0)

        self.video_url = None
        self.video_info = None
        self.thumbnail_photo = None
        self.available_qualities = ["Best quality", "Audio only"]
        self.quality_map = {}

        self.history_file = Path("history.json")
        self.history_data = []
        self.history_menu_visible = False

        self.load_history()
        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#E5E7EB",
            background=ACCENT_COLOR,
            bordercolor="#E5E7EB",
            lightcolor=ACCENT_COLOR,
            darkcolor=ACCENT_COLOR
        )

        self.main_container = tk.Frame(self.root, bg=BG_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=18, pady=18)

        title_label = tk.Label(
            self.main_container,
            text="Video Downloader",
            font=TITLE_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=(4, 14))

        self.input_card = tk.Frame(
            self.main_container,
            bg=CARD_COLOR,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            bd=0
        )
        self.input_card.pack(fill="x", padx=4, pady=(0, 12))

        self.input_frame = tk.Frame(self.input_card, bg=CARD_COLOR)
        self.input_frame.pack(fill="x", padx=18, pady=16)

        url_label = tk.Label(
            self.input_frame,
            text="Video URL",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT
        )
        url_label.pack(anchor="w", pady=(0, 6))

        self.url_entry = tk.Entry(
            self.input_frame,
            textvariable=self.url_var,
            font=BODY_FONT,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        self.url_entry.pack(fill="x", ipady=8)

        actions_row = tk.Frame(self.input_frame, bg=CARD_COLOR)
        actions_row.pack(fill="x", pady=(12, 0))

        self.fetch_button = tk.Button(
            actions_row,
            text="Fetch Info",
            font=BUTTON_FONT,
            width=16,
            command=self.fetch_video_info,
            bg=ACCENT_COLOR,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2"
        )
        self.fetch_button.pack(side="right")

        self.status_card = tk.Frame(self.main_container, bg=BG_COLOR)
        self.status_card.pack(fill="x", padx=4, pady=(0, 10))

        self.status_label = tk.Label(
            self.status_card,
            text="Ready for a video URL",
            fg=SUBTEXT_COLOR,
            bg=SOFT_BG,
            font=BODY_FONT,
            padx=12,
            pady=8,
            anchor="w",
            relief="flat"
        )
        self.status_label.pack(fill="x")

        self.details_frame = tk.Frame(self.main_container, bg=BG_COLOR)

        self.create_history_section()

        self.root.bind("<Button-1>", self.hide_history_context_menu, add="+")
        self.root.bind("<Escape>", self.hide_history_context_menu, add="+")

    def create_history_section(self):
        self.history_frame = tk.LabelFrame(
            self.main_container,
            text=" Download History ",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT,
            bd=1,
            relief="solid"
        )
        self.history_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        history_buttons_frame = tk.Frame(self.history_frame, bg=CARD_COLOR)
        history_buttons_frame.pack(fill="x", padx=14, pady=(12, 8))

        open_folder_button = tk.Button(
            history_buttons_frame,
            text="Open Selected Folder",
            command=self.open_selected_history_folder,
            bg=ACCENT_COLOR,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            font=BUTTON_FONT,
            width=18
        )
        open_folder_button.pack(side="left")

        clear_history_button = tk.Button(
            history_buttons_frame,
            text="Clear History",
            command=self.clear_history,
            bg=ERROR_COLOR,
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            font=BUTTON_FONT,
            width=14
        )
        clear_history_button.pack(side="right")

        self.history_listbox = tk.Listbox(
            self.history_frame,
            height=13,
            font=BODY_FONT,
            bg="white",
            fg=TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            selectbackground="#E0E7FF",
            selectforeground=TEXT_COLOR,
            activestyle="none"
        )
        self.history_listbox.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.history_listbox.bind("<Double-Button-1>", self.on_history_double_click)
        self.history_listbox.bind("<Button-3>", self.show_history_context_menu)

        self.history_menu = tk.Menu(self.root, tearoff=0)
        self.history_menu.add_command(label="Dosyayı Aç", command=self.menu_open_file)
        self.history_menu.add_command(label="Klasörü Aç", command=self.menu_open_folder)
        self.history_menu.add_separator()
        self.history_menu.add_command(label="History'den Kaldır", command=self.menu_remove_history_entry)

        self.refresh_history_listbox()

    def create_details_section(self):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        info_container = tk.Frame(
            self.details_frame,
            bg=CARD_COLOR,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            bd=0
        )
        info_container.pack(fill="x", padx=4, pady=(0, 12))

        self.thumbnail_label = tk.Label(
            info_container,
            text="No Thumbnail",
            width=220,
            height=124,
            relief="flat",
            bd=0,
            bg="#F3F4F6",
            fg=SUBTEXT_COLOR
        )
        self.thumbnail_label.pack(side="left", padx=16, pady=16)

        text_info_frame = tk.Frame(info_container, bg=CARD_COLOR)
        text_info_frame.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=16)

        meta_badge = tk.Label(
            text_info_frame,
            text="VIDEO DETAILS",
            bg="#EEF2FF",
            fg=ACCENT_COLOR,
            font=SMALL_FONT,
            padx=8,
            pady=4
        )
        meta_badge.pack(anchor="w", pady=(0, 10))

        self.title_info_label = tk.Label(
            text_info_frame,
            text="Title: -",
            anchor="w",
            justify="left",
            wraplength=460,
            font=INFO_TITLE_FONT,
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        )
        self.title_info_label.pack(fill="x", pady=(0, 10))

        self.channel_info_label = tk.Label(
            text_info_frame,
            text="Channel: -",
            anchor="w",
            justify="left",
            wraplength=460,
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR,
            font=INFO_FONT
        )
        self.channel_info_label.pack(fill="x", pady=(0, 8))

        self.duration_info_label = tk.Label(
            text_info_frame,
            text="Duration: -",
            anchor="w",
            justify="left",
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR,
            font=INFO_FONT
        )
        self.duration_info_label.pack(fill="x")

        options_frame = tk.LabelFrame(
            self.details_frame,
            text=" Download Options ",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT,
            bd=1,
            relief="solid"
        )
        options_frame.pack(fill="x", padx=4, pady=(0, 12))

        quality_label = tk.Label(
            options_frame,
            text="Download Quality",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT
        )
        quality_label.pack(anchor="w", padx=16, pady=(14, 6))

        self.quality_menu_frame = tk.Frame(options_frame, bg=CARD_COLOR)
        self.quality_menu_frame.pack(anchor="w", padx=16, pady=(0, 14))

        self.quality_dropdown = tk.OptionMenu(
            self.quality_menu_frame,
            self.quality_var,
            *self.available_qualities
        )
        self.quality_dropdown.pack(anchor="w")
        self.quality_dropdown.config(
            bg="white",
            fg=TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            activebackground="#F3F4F6",
            activeforeground=TEXT_COLOR,
            font=BODY_FONT,
            cursor="hand2",
            padx=10,
            pady=4
        )
        self.quality_dropdown["menu"].config(
            bg="white",
            fg=TEXT_COLOR,
            activebackground="#E0E7FF",
            activeforeground=TEXT_COLOR,
            font=BODY_FONT
        )

        folder_label = tk.Label(
            options_frame,
            text="Download Folder",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT
        )
        folder_label.pack(anchor="w", padx=16, pady=(0, 6))

        folder_entry_frame = tk.Frame(options_frame, bg=CARD_COLOR)
        folder_entry_frame.pack(fill="x", padx=16, pady=(0, 14))

        folder_entry = tk.Entry(
            folder_entry_frame,
            textvariable=self.download_folder,
            font=BODY_FONT,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        folder_entry.pack(side="left", fill="x", expand=True, ipady=7)

        browse_button = tk.Button(
            folder_entry_frame,
            text="Browse",
            command=self.select_folder,
            bg=ACCENT_COLOR,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            font=BUTTON_FONT,
            width=12
        )
        browse_button.pack(side="left", padx=(8, 0))

        progress_frame = tk.LabelFrame(
            self.details_frame,
            text=" Download Progress ",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=SECTION_FONT,
            bd=1,
            relief="solid"
        )
        progress_frame.pack(fill="x", padx=4, pady=(0, 12))

        self.progress_percent_label = tk.Label(
            progress_frame,
            text="0%",
            bg=CARD_COLOR,
            fg=ACCENT_COLOR,
            font=("Arial", 18, "bold")
        )
        self.progress_percent_label.pack(anchor="w", padx=16, pady=(14, 4))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 8))

        self.progress_info_label = tk.Label(
            progress_frame,
            text="Waiting to start",
            anchor="w",
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR,
            font=BODY_FONT
        )
        self.progress_info_label.pack(fill="x", padx=16, pady=(0, 14))

        button_row = tk.Frame(self.details_frame, bg=BG_COLOR)
        button_row.pack(fill="x", padx=4, pady=(0, 6))

        self.new_video_button = tk.Button(
            button_row,
            text="New Video",
            font=BUTTON_FONT,
            width=16,
            command=self.reset_to_input_view,
            bg="#6B7280",
            fg="white",
            activebackground="#4B5563",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.new_video_button.pack(side="left")

        self.download_button = tk.Button(
            button_row,
            text="Download",
            font=("Arial", 11, "bold"),
            width=18,
            command=self.download_video,
            bg=ACCENT_COLOR,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2"
        )
        self.download_button.pack(side="right")

    def set_status(self, text, kind="default"):
        if kind == "success":
            bg = "#ECFDF5"
            fg = SUCCESS_COLOR
        elif kind == "warning":
            bg = "#FFF7ED"
            fg = WARNING_COLOR
        elif kind == "error":
            bg = "#FEF2F2"
            fg = ERROR_COLOR
        else:
            bg = SOFT_BG
            fg = SUBTEXT_COLOR

        self.status_label.config(text=text, bg=bg, fg=fg)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as file:
                    self.history_data = json.load(file)
            except (json.JSONDecodeError, OSError):
                self.history_data = []
        else:
            self.history_data = []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as file:
                json.dump(self.history_data, file, indent=4, ensure_ascii=False)
        except OSError:
            messagebox.showerror("History Error", "Failed to save download history.")

    def add_to_history(self, title, download_type, quality, folder, file_path):
        entry = {
            "title": title,
            "type": download_type,
            "quality": quality,
            "folder": folder,
            "file_path": file_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.history_data.insert(0, entry)
        self.save_history()
        self.refresh_history_listbox()

    def refresh_history_listbox(self):
        if not hasattr(self, "history_listbox"):
            return

        self.history_listbox.delete(0, tk.END)

        if not self.history_data:
            self.history_listbox.insert(tk.END, "No downloads yet.")
            return

        for entry in self.history_data:
            title = entry["title"]
            if len(title) > 72:
                title = title[:69] + "..."
            line = f"{entry['time']}  •  {entry['type']}  •  {entry['quality']}  •  {title}"
            self.history_listbox.insert(tk.END, line)

    def clear_history(self):
        if not self.history_data:
            return

        confirm = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear download history?"
        )
        if not confirm:
            return

        self.history_data = []
        self.save_history()
        self.refresh_history_listbox()

    def get_selected_history_index(self):
        selection = self.history_listbox.curselection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select a history entry first.")
            return None

        index = selection[0]

        if not self.history_data or index >= len(self.history_data):
            messagebox.showerror("Error", "Invalid history selection.")
            return None

        return index

    def open_selected_history_file(self):
        index = self.get_selected_history_index()
        if index is None:
            return

        file_path_str = self.history_data[index].get("file_path", "").strip()

        if not file_path_str:
            messagebox.showerror("Error", "No file path found for this history entry.")
            return

        file_path = Path(file_path_str)

        if not file_path.exists():
            messagebox.showerror("Error", f"File does not exist:\n{file_path}")
            return

        try:
            subprocess.Popen(["xdg-open", str(file_path)])
        except Exception as e:
            messagebox.showerror("Open File Error", str(e))

    def open_selected_history_folder(self):
        index = self.get_selected_history_index()
        if index is None:
            return

        folder = self.history_data[index].get("folder", "").strip()

        if not folder:
            messagebox.showerror("Error", "No folder path found for this history entry.")
            return

        folder_path = Path(folder)

        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder does not exist:\n{folder}")
            return

        try:
            subprocess.Popen(["xdg-open", str(folder_path)])
        except Exception as e:
            messagebox.showerror("Open Folder Error", str(e))

    def remove_selected_history_entry(self):
        index = self.get_selected_history_index()
        if index is None:
            return

        confirm = messagebox.askyesno(
            "Remove History Entry",
            "Remove the selected entry from history?"
        )
        if not confirm:
            return

        self.history_data.pop(index)
        self.save_history()
        self.refresh_history_listbox()

    def on_history_double_click(self, event):
        self.open_selected_history_folder()

    def hide_history_context_menu(self, event=None):
        if self.history_menu_visible:
            try:
                self.history_menu.unpost()
            except Exception:
                pass
            self.history_menu_visible = False

    def menu_open_file(self):
        self.hide_history_context_menu()
        self.open_selected_history_file()

    def menu_open_folder(self):
        self.hide_history_context_menu()
        self.open_selected_history_folder()

    def menu_remove_history_entry(self):
        self.hide_history_context_menu()
        self.remove_selected_history_entry()

    def show_history_context_menu(self, event):
        if not self.history_data:
            return

        index = self.history_listbox.nearest(event.y)

        if index < 0 or index >= len(self.history_data):
            return

        self.hide_history_context_menu()

        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(index)
        self.history_listbox.activate(index)

        try:
            self.history_menu_visible = True
            self.history_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.history_menu.grab_release()

    def update_quality_dropdown(self):
        menu = self.quality_dropdown["menu"]
        menu.delete(0, "end")

        for quality in self.available_qualities:
            menu.add_command(
                label=quality,
                command=lambda value=quality: self.quality_var.set(value)
            )

        self.quality_var.set(self.available_qualities[0])

    def extract_available_qualities(self, info):
        formats = info.get("formats", [])
        quality_map = {}

        def is_compatible_video(fmt):
            vcodec = (fmt.get("vcodec") or "").lower()
            ext = (fmt.get("ext") or "").lower()

            if not fmt.get("height") or not fmt.get("format_id"):
                return False

            if not vcodec or vcodec == "none":
                return False

            if ext != "mp4":
                return False

            return (
                "avc1" in vcodec or
                "h264" in vcodec or
                "hev1" in vcodec or
                "h265" in vcodec or
                "hevc" in vcodec
            )

        def codec_score(fmt):
            vcodec = (fmt.get("vcodec") or "").lower()

            if "avc1" in vcodec:
                return 1000
            if "h264" in vcodec:
                return 900
            if "hev1" in vcodec or "h265" in vcodec or "hevc" in vcodec:
                return 700
            return 0

        grouped = {}

        for fmt in formats:
            if not is_compatible_video(fmt):
                continue

            label = f"{fmt['height']}p"
            grouped.setdefault(label, []).append(fmt)

        for label, candidates in grouped.items():
            best_candidate = max(candidates, key=codec_score)
            quality_map[label] = best_candidate["format_id"]

        sorted_labels = sorted(quality_map.keys(), key=lambda x: int(x[:-1]))
        qualities = ["Best quality", "Audio only"] + sorted_labels

        return qualities, quality_map

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_folder.set(folder)

    def get_format_option(self):
        selected_quality = self.quality_var.get()

        if selected_quality == "Best quality":
            return "(bv*[vcodec~='^((he|a)vc|h26[45])'][ext=mp4]+ba[ext=m4a])/(b[ext=mp4])/(bv*+ba/b)"

        if selected_quality == "Audio only":
            return "bestaudio/best"

        if selected_quality in self.quality_map:
            format_id = self.quality_map[selected_quality]
            return f"{format_id}+ba[ext=m4a]/{format_id}+bestaudio/{format_id}"

        return "(bv*[vcodec~='^((he|a)vc|h26[45])'][ext=mp4]+ba[ext=m4a])/(b[ext=mp4])/(bv*+ba/b)"

    def format_duration(self, seconds):
        if not seconds:
            return "-"

        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}:{minutes:02}:{sec:02}"
        return f"{minutes}:{sec:02}"

    def load_thumbnail(self, thumbnail_url):
        if not thumbnail_url:
            self.thumbnail_label.config(image="", text="No Thumbnail")
            return

        try:
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()

            image_data = BytesIO(response.content)
            image = Image.open(image_data)

            target_width = 220
            target_height = 124

            img_width, img_height = image.size
            img_ratio = img_width / img_height
            target_ratio = target_width / target_height

            if img_ratio > target_ratio:
                new_height = target_height
                new_width = int(new_height * img_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / img_ratio)

            image = image.resize((new_width, new_height))

            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height

            image = image.crop((left, top, right, bottom))

            self.thumbnail_photo = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_photo, text="")
        except Exception:
            self.thumbnail_label.config(image="", text="Thumbnail\nUnavailable")

    def fetch_video_info(self):
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL first.")
            return

        self.set_status("Fetching video info...", "warning")
        self.root.update_idletasks()

        info_opts = {
            "quiet": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.video_url = url
            self.video_info = info
            self.available_qualities, self.quality_map = self.extract_available_qualities(info)

            self.input_card.pack_forget()
            self.history_frame.pack_forget()

            if not self.details_frame.winfo_ismapped():
                self.create_details_section()
                self.details_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

            self.update_quality_dropdown()

            title = info.get("title", "Unknown title")
            channel = info.get("uploader") or info.get("channel") or "Unknown channel"
            duration = self.format_duration(info.get("duration"))
            thumbnail_url = info.get("thumbnail")

            self.title_info_label.config(text=title)
            self.channel_info_label.config(text=f"Channel: {channel}")
            self.duration_info_label.config(text=f"Duration: {duration}")

            self.progress_var.set(0)
            self.progress_percent_label.config(text="0%")
            self.progress_info_label.config(text="Waiting to start")

            self.load_thumbnail(thumbnail_url)

            self.set_status("Video info fetched successfully.", "success")

        except Exception as e:
            self.set_status("Failed to fetch video info.", "error")
            messagebox.showerror("Info Error", str(e))

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded_bytes = d.get("downloaded_bytes", 0)

            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                self.progress_var.set(percent)
                self.progress_percent_label.config(text=f"{percent:.0f}%")

                speed = d.get("speed")
                eta = d.get("eta")

                speed_text = f"{speed / 1024 / 1024:.2f} MiB/s" if speed else "Unknown speed"
                eta_text = f"{eta} sec" if eta is not None else "Unknown ETA"

                self.progress_info_label.config(
                    text=f"Speed: {speed_text}   •   ETA: {eta_text}"
                )
            else:
                self.progress_info_label.config(text="Downloading...")
            self.root.update_idletasks()

        elif d["status"] == "finished":
            self.progress_var.set(100)
            self.progress_percent_label.config(text="100%")
            self.progress_info_label.config(text="Download finished. Processing file...")
            self.root.update_idletasks()

    def reset_to_input_view(self):
        self.video_url = None
        self.video_info = None
        self.url_var.set("")
        self.download_folder.set("")
        self.quality_var.set("Best quality")
        self.progress_var.set(0)
        self.available_qualities = ["Best quality", "Audio only"]
        self.quality_map = {}

        if hasattr(self, "progress_info_label"):
            self.progress_info_label.config(text="Waiting to start")

        if hasattr(self, "progress_percent_label"):
            self.progress_percent_label.config(text="0%")

        if hasattr(self, "title_info_label"):
            self.title_info_label.config(text="Title: -")

        if hasattr(self, "channel_info_label"):
            self.channel_info_label.config(text="Channel: -")

        if hasattr(self, "duration_info_label"):
            self.duration_info_label.config(text="Duration: -")

        if hasattr(self, "thumbnail_label"):
            self.thumbnail_label.config(image="", text="No Thumbnail")

        self.thumbnail_photo = None

        self.details_frame.pack_forget()
        self.input_card.pack(fill="x", padx=4, pady=(0, 12))
        self.history_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        self.set_status("Ready for a video URL", "default")
        self.url_entry.focus_set()

    def build_final_file_path(self, folder, title, is_audio_only):
        safe_title = sanitize_filename(title, restricted=False)
        extension = "mp3" if is_audio_only else "mp4"
        return str(Path(folder) / f"{safe_title}.{extension}")

    def download_video(self):
        folder = self.download_folder.get().strip()

        if not self.video_url:
            messagebox.showerror("Error", "Please fetch video info first.")
            return

        if not folder:
            messagebox.showerror("Error", "Please select a download folder.")
            return

        self.progress_var.set(0)
        self.progress_percent_label.config(text="0%")
        self.progress_info_label.config(text="Starting download...")
        self.set_status("Downloading...", "warning")
        self.download_button.config(state="disabled")
        self.fetch_button.config(state="disabled")
        self.root.update_idletasks()

        selected_quality = self.quality_var.get()
        video_title = self.video_info.get("title", "Unknown title") if self.video_info else "Unknown title"

        ydl_opts = {
            "outtmpl": str(Path(folder) / "%(title)s.%(ext)s"),
            "format": self.get_format_option(),
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            "merge_output_format": "mp4",
        }

        is_audio_only = selected_quality == "Audio only"

        if is_audio_only:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])

            self.set_status("Download completed successfully.", "success")
            self.progress_percent_label.config(text="100%")
            self.progress_info_label.config(text="Completed")

            download_type = "MP3" if is_audio_only else "Video"
            final_file_path = self.build_final_file_path(folder, video_title, is_audio_only)

            self.add_to_history(
                video_title,
                download_type,
                selected_quality,
                folder,
                final_file_path
            )

            if is_audio_only:
                messagebox.showinfo("Success", f"MP3 downloaded successfully to:\n{folder}")
            else:
                messagebox.showinfo("Success", f"Video downloaded successfully to:\n{folder}")

        except Exception as e:
            error_message = str(e)

            if "ffmpeg is not installed" in error_message.lower():
                error_message = "Merged video/audio downloads require ffmpeg. Please install ffmpeg first."

            self.set_status("Download failed.", "error")
            self.progress_info_label.config(text="Download failed.")
            messagebox.showerror("Download Error", error_message)

        finally:
            self.download_button.config(state="normal")
            self.fetch_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()