import json
import os

json_path = "indexes.json"
macro_path = os.path.join(".", "Macros")

current_json = json.load(json_path)

for filename in os.listdir(macro_path):
    try:
