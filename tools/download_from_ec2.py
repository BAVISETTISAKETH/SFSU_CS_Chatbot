"""
Simple script to download the scraped data from EC2
"""

import paramiko
import os
from tqdm import tqdm

# Connection details
hostname = "3.145.143.107"
username = "ubuntu"
key_path = r"C:\Users\bavis\Downloads\sfsu-scraper-key.pem"
remote_file = "/home/ubuntu/data/comprehensive_sfsu_crawl.json"
local_file = r"D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json"

print("Connecting to EC2...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh.connect(hostname, username=username, pkey=key)

print("Connected! Starting download...")
sftp = ssh.open_sftp()

# Get file size
file_size = sftp.stat(remote_file).st_size
print(f"File size: {file_size / 1024 / 1024:.2f} MB")

# Download with progress bar
with tqdm(total=file_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
    def callback(transferred, total):
        pbar.update(transferred - pbar.n)

    sftp.get(remote_file, local_file, callback=callback)

sftp.close()
ssh.close()

print(f"\nDownload complete! File saved to: {local_file}")
print(f"File size: {os.path.getsize(local_file) / 1024 / 1024:.2f} MB")
