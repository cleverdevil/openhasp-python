from importlib.resources import files

icons = {}

codepoints_file = files(__package__) / "icons.codepoints"
with codepoints_file.open("r") as f:
    for line in f.readlines():
        key, point = line.strip().split(" ")
        icons[key] = point


def get(key):
    codepoint = icons.get(key)
    return chr(int(codepoint, 16))
