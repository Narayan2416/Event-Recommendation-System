import gdown

file_id = "1XwPru0cYrd72nA-2crIG9Vn5jpfPnCON"
url = f"https://drive.google.com/uc?id={file_id}"
output = "expo_model.pkl"

gdown.download(url, output, quiet=False)