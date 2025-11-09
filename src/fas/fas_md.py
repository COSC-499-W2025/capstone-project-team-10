class Markdown:
    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.markdown_block = f.read()