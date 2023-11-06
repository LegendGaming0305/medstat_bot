import json

def json_reader():
    with open(r"non-script-files\priority_list.json", 'r', encoding="utf-8") as j_file:
        return json.load(j_file)

info = json_reader()
print(info)
print(info["OWNER"])
print(info)
