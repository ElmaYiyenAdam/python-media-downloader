from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("620x540")
        self.root.minsize(620, 540)
        self.root.resizable(True, True)

        self.download_folder = tk.StringVar()
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="Best quality")
        self.progress_var = tk.DoubleVar(value=0)

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Video Downloader",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=15)

        url_frame = tk.Frame(self.root)
        url_frame.pack(fill="x", padx=20, pady=10)

        url_label = tk.Label(url_frame, text="Video URL:")
        url_label.pack(anchor="w")

        url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(fill="x", pady=5)

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(fill="x", padx=20, pady=10)

        folder_label = tk.Label(folder_frame, text="Download Folder:")
        folder_label.pack(anchor="w")

        folder_entry_frame = tk.Frame(folder_frame)
        folder_entry_frame.pack(fill="x", pady=5)

        folder_entry = tk.Entry(
            folder_entry_frame,
            textvariable=self.download_folder,
            width=45
        )
        folder_entry.pack(side="left", fill="x", expand=True)

        browse_button = tk.Button(
            folder_entry_frame,
            text="Browse",
            command=self.select_folder
        )
        browse_button.pack(side="left", padx=5)

        quality_frame = tk.Frame(self.root)
        quality_frame.pack(fill="x", padx=20, pady=10)

        quality_label = tk.Label(quality_frame, text="Download Quality:")
        quality_label.pack(anchor="w")

        quality_options = [
            "Best quality",
            "Audio only",
            "720p",
            "1080p"
        ]

        quality_menu = tk.OptionMenu(
            quality_frame,
            self.quality_var,
            *quality_options
        )
        quality_menu.pack(anchor="w", pady=5)

        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=10)

        progress_title = tk.Label(progress_frame, text="Download Progress:")
        progress_title.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=5)

        self.progress_info_label = tk.Label(
            progress_frame,
            text="0%",
            font=("Arial", 10)
        )
        self.progress_info_label.pack(anchor="w")

        self.status_label = tk.Label(
            self.root,
            text="Ready",
            fg="blue",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=15)

        self.download_button = tk.Button(
            self.root,
            text="Download",
            font=("Arial", 11, "bold"),
            width=20,
            command=self.download_video
        )
        self.download_button.pack(pady=25)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_folder.set(folder)

    def get_format_option(self):
        quality = self.quality_var.get()

        if quality == "Best quality":
            return "best"
        elif quality == "Audio only":
            return "bestaudio"
        elif quality == "720p":
            return "bestvideo[height<=720]+bestaudio/best"
        elif quality == "1080p":
            return "bestvideo[height<=1080]+bestaudio/best"
        else:
            return "best"

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

    def download_video(self):
        url = self.url_var.get().strip()
        folder = self.download_folder.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        if not folder:
            messagebox.showerror("Error", "Please select a download folder.")
            return

        self.progress_var.set(0)
        self.progress_info_label.config(text="Starting download...")
        self.status_label.config(text="Downloading...", fg="orange")
        self.download_button.config(state="disabled")
        self.root.update_idletasks()

        ydl_opts = {
            "outtmpl": str(Path(folder) / "%(title)s.%(ext)s"),
            "format": self.get_format_option(),
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.config(text="Download completed successfully!", fg="green")
            self.progress_info_label.config(text="100% | Completed")
            messagebox.showinfo("Success", f"Downloaded successfully to:\n{folder}")

        except Exception as e:
            self.status_label.config(text="Download failed.", fg="red")
            self.progress_info_label.config(text="Download failed.")
            messagebox.showerror("Download Error", str(e))

        finally:
            self.download_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()