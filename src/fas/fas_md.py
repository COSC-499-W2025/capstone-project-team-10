import mrkdwn_analysis
from src.fas.fas_text_analysis import TextSummary


class Markdown:

    def __init__(self, path):
        self.analyzer = mrkdwn_analysis.MarkdownAnalyzer(path)
        self.md_path = path

    def get_headers(self) -> dict[str, list[str]]:
        # Utilize the identify_headers() to extract the information of all headers
        return self.analyzer.identify_headers()

    def get_header_hierarchy(self) -> list:
        headers = self.get_headers().get("Header", [])
        root = []
        if not headers:
            return root
        stack = [(0, root)]  # (level, current_list)

        for h in headers:
            level = int(h["level"])
            text = h["text"]
            node = {"title": text, "children": []}

            # move up until parent level
            while stack and stack[-1][0] >= level:
                stack.pop()

            # attach to current parent list
            stack[-1][1].append(node)
            stack.append((level, node["children"]))

        return root

    def get_word_counts(self) -> int:
        # Output: (int) number of word counts within the .md
        return self.analyzer.count_words()

    def get_code_blocks(self) -> dict:
        # Return all the code blocks within the .md
        return self.analyzer.identify_code_blocks()

    def get_paragraphs(self):
        text = self.analyzer.identify_paragraphs()
        analyzer = TextSummary(text) if text.strip() else None
        sentiment = analyzer.getSentiment()
        return