from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import requests
from PIL import Image, ImageTk
import yt_dlp


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("720x760")
        self.root.minsize(720, 760)
        self.root.resizable(True, True)

        self.url_var = tk.StringVar()
        self.download_folder = tk.StringVar()
        self.quality_var = tk.StringVar(value="Best quality")
        self.progress_var = tk.DoubleVar(value=0)

        self.video_url = None
        self.thumbnail_photo = None

        self.build_ui()

    def build_ui(self):
        title_label = tk.Label(
            self.root,
            text="Video Downloader",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=25, pady=10)

        url_label = tk.Label(self.input_frame, text="Video URL:")
        url_label.pack(anchor="w")

        self.url_entry = tk.Entry(self.input_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(fill="x", pady=8)

        self.fetch_button = tk.Button(
            self.input_frame,
            text="Fetch Info",
            font=("Arial", 11, "bold"),
            width=18,
            command=self.fetch_video_info
        )
        self.fetch_button.pack(anchor="e", pady=8)

        self.status_label = tk.Label(
            self.root,
            text="Enter a URL and fetch video info.",
            fg="blue",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=6)

        self.details_frame = tk.Frame(self.root)

    def create_details_section(self):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        info_container = tk.Frame(self.details_frame)
        info_container.pack(fill="x", padx=10, pady=10)

        self.thumbnail_label = tk.Label(
            info_container,
            text="No Thumbnail",
            width=30,
            height=10,
            relief="solid",
            bd=1
        )
        self.thumbnail_label.pack(side="left", padx=10, pady=10)

        text_info_frame = tk.Frame(info_container)
        text_info_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.title_info_label = tk.Label(
            text_info_frame,
            text="Title: -",
            anchor="w",
            justify="left",
            wraplength=380,
            font=("Arial", 11, "bold")
        )
        self.title_info_label.pack(fill="x", pady=6)

        self.channel_info_label = tk.Label(
            text_info_frame,
            text="Channel: -",
            anchor="w",
            justify="left",
            wraplength=380
        )
        self.channel_info_label.pack(fill="x", pady=6)

        self.duration_info_label = tk.Label(
            text_info_frame,
            text="Duration: -",
            anchor="w",
            justify="left"
        )
        self.duration_info_label.pack(fill="x", pady=6)

        options_frame = tk.LabelFrame(self.details_frame, text="Download Options")
        options_frame.pack(fill="x", padx=10, pady=15)

        quality_label = tk.Label(options_frame, text="Download Quality:")
        quality_label.pack(anchor="w", padx=12, pady=(12, 4))

        quality_options = [
            "Best quality",
            "Audio only",
            "720p",
            "1080p"
        ]

        quality_menu = tk.OptionMenu(
            options_frame,
            self.quality_var,
            *quality_options
        )
        quality_menu.pack(anchor="w", padx=12, pady=(0, 12))

        folder_label = tk.Label(options_frame, text="Download Folder:")
        folder_label.pack(anchor="w", padx=12, pady=(0, 4))

        folder_entry_frame = tk.Frame(options_frame)
        folder_entry_frame.pack(fill="x", padx=12, pady=(0, 12))

        folder_entry = tk.Entry(
            folder_entry_frame,
            textvariable=self.download_folder
        )
        folder_entry.pack(side="left", fill="x", expand=True)

        browse_button = tk.Button(
            folder_entry_frame,
            text="Browse",
            command=self.select_folder
        )
        browse_button.pack(side="left", padx=6)

        progress_frame = tk.LabelFrame(self.details_frame, text="Download Progress")
        progress_frame.pack(fill="x", padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x", padx=12, pady=(12, 6))

        self.progress_info_label = tk.Label(
            progress_frame,
            text="0%",
            anchor="w"
        )
        self.progress_info_label.pack(fill="x", padx=12, pady=(0, 12))

        self.new_video_button = tk.Button(
            self.details_frame,
            text="New Video",
            font=("Arial", 10, "bold"),
            width=16,
            command=self.reset_to_input_view
        )
        self.new_video_button.pack(pady=(10, 8))

        self.download_button = tk.Button(
            self.details_frame,
            text="Download",
            font=("Arial", 11, "bold"),
            width=20,
            command=self.download_video
        )
        self.download_button.pack(pady=20)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_folder.set(folder)


    def get_format_option(self):
        quality = self.quality_var.get()

        if quality == "Best quality":
            return "bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/best[vcodec^=avc1][ext=mp4]/best[ext=mp4]/best"
        if quality == "Audio only":
            return "bestaudio[ext=m4a]/bestaudio/best"
        if quality == "720p":
            return "bestvideo[height<=720][vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][vcodec^=avc1][ext=mp4]/best[height<=720][ext=mp4]/best"
        if quality == "1080p":
            return "bestvideo[height<=1080][vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][vcodec^=avc1][ext=mp4]/best[height<=1080][ext=mp4]/best"

        return "bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/best[vcodec^=avc1][ext=mp4]/best[ext=mp4]/best"

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
            image.thumbnail((220, 220))

            self.thumbnail_photo = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_photo, text="")
        except Exception:
            self.thumbnail_label.config(image="", text="Thumbnail\nUnavailable")

    def fetch_video_info(self):
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL first.")
            return

        self.status_label.config(text="Fetching video info...", fg="orange")
        self.root.update_idletasks()

        info_opts = {
            "quiet": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.video_url = url
            self.input_frame.pack_forget()

            if not self.details_frame.winfo_ismapped():
                self.create_details_section()
                self.details_frame.pack(fill="both", expand=True, padx=20, pady=10)

            title = info.get("title", "Unknown title")
            channel = info.get("uploader") or info.get("channel") or "Unknown channel"
            duration = self.format_duration(info.get("duration"))
            thumbnail_url = info.get("thumbnail")

            self.title_info_label.config(text=f"Title: {title}")
            self.channel_info_label.config(text=f"Channel: {channel}")
            self.duration_info_label.config(text=f"Duration: {duration}")

            self.progress_var.set(0)
            self.progress_info_label.config(text="0%")

            self.load_thumbnail(thumbnail_url)

            self.status_label.config(text="Video info fetched successfully.", fg="green")

        except Exception as e:
            self.status_label.config(text="Failed to fetch video info.", fg="red")
            messagebox.showerror("Info Error", str(e))

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded_bytes = d.get("downloaded_bytes", 0)

            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                self.progress_var.set(percent)

                speed = d.get("speed")
                eta = d.get("eta")

                speed_text = f"{speed / 1024 / 1024:.2f} MiB/s" if speed else "Unknown speed"
                eta_text = f"{eta} sec" if eta is not None else "Unknown ETA"

                self.progress_info_label.config(
                    text=f"{percent:.1f}% | Speed: {speed_text} | ETA: {eta_text}"
                )
            else:
                self.progress_info_label.config(text="Downloading...")

            self.root.update_idletasks()

        elif d["status"] == "finished":
            self.progress_var.set(100)
            self.progress_info_label.config(text="Download finished. Processing file...")
            self.root.update_idletasks()

    def reset_to_input_view(self):
        self.video_url = None
        self.url_var.set("")
        self.download_folder.set("")
        self.quality_var.set("Best quality")
        self.progress_var.set(0)

        if hasattr(self, "progress_info_label"):
            self.progress_info_label.config(text="0%")

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
        self.input_frame.pack(fill="x", padx=25, pady=10)

        self.status_label.config(text="Enter a URL and fetch video info.", fg="blue")
        self.url_entry.focus_set()

    def download_video(self):
        folder = self.download_folder.get().strip()

        if not self.video_url:
            messagebox.showerror("Error", "Please fetch video info first.")
            return

        if not folder:
            messagebox.showerror("Error", "Please select a download folder.")
            return

        self.progress_var.set(0)
        self.progress_info_label.config(text="Starting download...")
        self.status_label.config(text="Downloading...", fg="orange")
        self.download_button.config(state="disabled")
        self.fetch_button.config(state="disabled")
        self.root.update_idletasks()

        ydl_opts = {
            "outtmpl": str(Path(folder) / "%(title)s.%(ext)s"),
            "format": self.get_format_option(),
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            "merge_output_format": "mp4",
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])

            self.status_label.config(text="Download completed successfully!", fg="green")
            self.progress_info_label.config(text="100% | Completed")
            messagebox.showinfo("Success", f"Downloaded successfully to:\n{folder}")

        except Exception as e:
            error_message = str(e)

            if "ffmpeg is not installed" in error_message.lower():
                error_message = "Merged video downloads require ffmpeg. Please install ffmpeg first."

            self.status_label.config(text="Download failed.", fg="red")
            self.progress_info_label.config(text="Download failed.")
            messagebox.showerror("Download Error", error_message)

        finally:
            self.download_button.config(state="normal")
            self.fetch_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()