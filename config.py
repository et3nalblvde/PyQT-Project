import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

posters = BASE_DIR /"posters"
users = BASE_DIR /"Database"/"users.csv"
data = BASE_DIR /"Database"
icons = BASE_DIR /"icons"

posters = str(posters).replace("\\", "/")
users = str(users).replace("\\", "/")
data = str(data).replace("\\", "/")
icons = str(icons).replace("\\", "/")

print("BASE_DIR:", BASE_DIR)
print("Database path exists:", (BASE_DIR / "Database").exists())
print("Users path exists:", (BASE_DIR / "Database" / "users.csv").exists())
print(posters, users, icons,data, sep='\n')
