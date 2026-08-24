"""Script to download raw MetroPT Compressor dataset from Kaggle.

Dataset: MetroPT-3 (Compressor Fault Diagnosis & Predictive Maintenance)
Kaggle Slug: nelson17/metropt3-dataset or hafiznouman77/metropt-3-dataset-compressor-fault-diagnosis
"""

import os
import sys
import subprocess


def download_from_kaggle(dataset_slug: str = "nelson17/metropt3-dataset", target_dir: str = "knowledge/datasets/raw"):
    """
    Download raw dataset from Kaggle via kagglehub or kaggle CLI.
    Requires ~/.kaggle/kaggle.json or KAGGLE_USERNAME / KAGGLE_KEY environment variables.
    """
    os.makedirs(target_dir, exist_ok=True)
    print(f"[*] Target dataset: {dataset_slug}")
    print(f"[*] Target directory: {target_dir}")

    # Check for kagglehub
    try:
        import kagglehub
        print("[*] Downloading using kagglehub...")
        path = kagglehub.dataset_download(dataset_slug)
        print(f"[+] Download completed! Files located at: {path}")
        return path
    except ImportError:
        pass

    # Check for kaggle CLI
    try:
        cmd = ["kaggle", "datasets", "download", "-d", dataset_slug, "-p", target_dir, "--unzip"]
        print(f"[*] Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Output:", result.stdout)
        return target_dir
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[!] Kaggle CLI not found or returned error: {e}")
        print("\nTo download full multi-GB raw dataset from Kaggle:")
        print("1. Install kaggle: pip install kaggle")
        print("2. Place kaggle.json in ~/.kaggle/ (or C:/Users/<User>/.kaggle/kaggle.json)")
        print(f"3. Run: kaggle datasets download -d {dataset_slug} --unzip -p {target_dir}")
        return None


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "nelson17/metropt3-dataset"
    download_from_kaggle(slug)
