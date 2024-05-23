import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_PATH = os.path.join(os.getcwd(), "static", "images")
os.getcwd()
print(UPLOAD_PATH)
print(os.path.join("../static", "images"))

# os.makedirs(UPLOAD_PATH, exist_ok=True)
# now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
# file_name = now + file.filename
# save_path = os.path.join(UPLOAD_PATH, file_name)

