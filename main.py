from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("520x450")
        self.root.resizable(True, True)

        self.download_folder = tk.StringVar()
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="Best quality")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Video Downloader",
            font=("Arial", 16, "bold")
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

        self.status_label = tk.Label(
            self.root,
            text="Ready",
            fg="blue",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=15)

        download_button = tk.Button(
            self.root,
            text="Download",
            font=("Arial", 11, "bold"),
            width=20,
            command=self.download_video
        )
        download_button.pack(pady=10)

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

    def download_video(self):
        url = self.url_var.get().strip()
        folder = self.download_folder.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        if not folder:
            messagebox.showerror("Error", "Please select a download folder.")
            return

        self.status_label.config(text="Downloading...", fg="orange")
        self.root.update_idletasks()

        ydl_opts = {
            "outtmpl": str(Path(folder) / "%(title)s.%(ext)s"),
            "format": self.get_format_option(),
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.config(text="Download completed successfully!", fg="green")
            messagebox.showinfo("Success", f"Downloaded successfully to:\n{folder}")

        except Exception as e:
            self.status_label.config(text="Download failed.", fg="red")
            messagebox.showerror("Download Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()