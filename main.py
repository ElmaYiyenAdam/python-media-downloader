from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import yt_dlp


def select_download_folder() -> Path:
    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(title="Select Download Folder")
    if not folder:
        raise SystemExit("No folder selected. Program terminated.")

    return Path(folder)


def get_quality_options() -> str:
    print("\nSelect download quality:")
    print("1. Best quality")
    print("2. Audio only")
    print("3. Custom video resolution")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        return "best"
    elif choice == "2":
        return "bestaudio"
    elif choice == "3":
        resolution = input("Enter maximum resolution (e.g. 1080 or 720): ").strip()

        if not resolution.isdigit():
            print("Invalid resolution. Defaulting to best quality.")
            return "best"

        return f"bestvideo[height<={resolution}]+bestaudio/best"
    else:
        print("Invalid choice. Defaulting to best quality.")
        return "best"


def main():
    download_folder = select_download_folder()
    selected_format = get_quality_options()
    url = input("\nEnter URL: ").strip()

    if not url:
        raise SystemExit("No URL entered. Program terminated.")

    ydl_opts = {
        "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
        "format": selected_format,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\nDownload completed successfully: {download_folder}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()