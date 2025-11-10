import mrkdwn_analysis

class Markdown:
    def __init__(self, path):
        self.analyzer = mrkdwn_analysis.MarkdownAnalyzer(path)
        self.md_path = path

    def get_headers(self):
        """
            Utilize the identify_headers() to extract the information of all headers

            Output:
                (list) that collects all the headers, including their levels, titles, positioning within the md etc.

            Example:
                print(test_markdown.get_headers())
                >>
                'Header':
                [{'line': 1, 'level': 1, 'text': 'Project Overview'},
                {'line': 11, 'level': 2, 'text': 'Introduction'},
                {'line': 18, 'level': 3, 'text': 'Background'},
                ...
        """
        return self.analyzer.identify_headers()

    def get_header_hierarchy(self):
        r"""
            Convert mrkdown-analysis identify_headers() output
            into a nested dictionary based on header levels.

            Output:
                (dict(list)) that is nested, based on the levels of headings size, into a nested dictionary. Should be easily processed by the machine

            Example:
                print(test_markdown.get_header_hierarchy())
                >>
                [
                    {
                        "title": "Project Overview",
                        "children": [
                        {
                            "title": "Introduction",
                            "children": [
                                    {"title": "Background", "children": []},
                                    {"title": "Objectives", "children": []}
                ...
        """
        headers = self.get_headers()["Header"]
        root = []
        stack = [(0, root)]  # (level, current_list)

        for h in headers:
            level, text = h["level"], h["text"]
            node = {"title": text, "children": []}

            # move up until parent level
            while stack and stack[-1][0] >= level:
                stack.pop()

            # attach to current parent list
            stack[-1][1].append(node)
            stack.append((level, node["children"]))

        return root

    def get_word_counts(self):
        """
            Return the numbers of word counts within the .md

            Output:
                (int) number of word counts within the .md
        """
        return self.analyzer.count_words()

    def get_code_blocks(self):
        """
            Return all the code blocks within the .md

            Output:
                (dict) as shown in the example

            Example:
                print(test_markdown.get_code_blocks())
                >> {'Code block':
                    [{'start_line': 47, 'content': 'import pandas as pd\ndf = pd.read_csv("data/input.csv")\ndf.head()', 'language': 'python'},
                    {'start_line': 63, 'content': 'summary(df)\nplot(df$value)', 'language': 'r'}]}
        """
        return self.analyzer.identify_code_blocks()

    def get_paragraphs(self):
        """
            Return all the paragraphs within the .md

            Output:
                (dict) as shown in the example

            Example:
                print(test_markdown.get_paragraphs())
                >>
                {'Paragraph':
                ['This document tests **mrkdown-analysis** parsing capabilities.',
                '`mrkdown-analysis` aims to:',
                'Markdown is a lightweight format.  \nExample inline code: `print("Hello, world!")`',
                '![Chart Example](https://dummyimage.com/600x400/000/fff&text=Chart+Placeholder)']}
        """
        return self.analyzer.identify_paragraphs()

    # Note - there is so much more that markdown-analysis can do - but there's also a few that it cannot do.
    # Have to congregate a meetings to discuss what (more) is needed to extract from an .md, but for now, this should do.

"""
# Usage
test_markdown = Markdown("test_markdown.md")
hierarchy = test_markdown.get_paragraphs()
print(hierarchy)
"""
