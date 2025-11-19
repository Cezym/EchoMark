import os
import requests
import zipfile
import shutil

def download_data(data_dir="src/data"):
    os.makedirs(data_dir, exist_ok=True)

    URLS = {
        "audio_mono-mic.zip": "https://zenodo.org/records/3371780/files/audio_mono-mic.zip?download=1",
        "groove-v1.0.0.zip":  "https://storage.googleapis.com/magentadata/datasets/groove/groove-v1.0.0.zip",
    }

    guitar_dir = os.path.join(data_dir, "guitar")
    groove_dir = os.path.join(data_dir, "groove")

    os.makedirs(guitar_dir, exist_ok=True)
    os.makedirs(groove_dir, exist_ok=True)

    for filename, url in URLS.items():

        zip_path = os.path.join(data_dir, filename)

        print(f"\nDownloading {filename}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Extracting {filename}...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            members = zip_ref.namelist()

            # --- 1. audio_mono-mic.zip -> extract to guitar/ ---
            if filename == "audio_mono-mic.zip":
                zip_ref.extractall(guitar_dir)

            # --- 2. groove-v1.0.0.zip -> extract only wav ---
            elif filename == "groove-v1.0.0.zip":
                for member in members:
                    if member.lower().endswith(".wav"):
                        zip_ref.extract(member, groove_dir)

                        # "member" includes folders, so flatten:
                        extracted_path = os.path.join(groove_dir, member)
                        final_path = os.path.join(groove_dir, os.path.basename(member))

                        shutil.move(extracted_path, final_path)

                for root, dirs, files in os.walk(groove_dir, topdown=False):
                    for d in dirs:
                        full = os.path.join(root, d)
                        if full != groove_dir:
                            shutil.rmtree(full, ignore_errors=True)

        print(f"Removing ZIP: {filename}")
        os.remove(zip_path)

    print("\n✓ All downloads completed.")


if __name__ == "__main__":
    download_data()
