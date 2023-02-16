import wget, os, zipfile

# url = "https://chromedriver.storage.googleapis.com/111.0.5563.19/chromedriver_win32.zip"

# wget.download(url, os.getcwd())

# Unzip File
with zipfile.ZipFile(os.getcwd() + "\\chromedriver_win32.zip", 'r') as zip_ref:
    zip_ref.extractall(os.getcwd())
