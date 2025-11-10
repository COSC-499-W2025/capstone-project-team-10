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

"""
# Usage
test_markdown = Markdown("test_markdown.md")
hierarchy = test_markdown.get_headers()
print(hierarchy)
"""