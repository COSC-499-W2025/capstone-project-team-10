import mrkdwn_analysis


class Markdown:
    """
    A class that holds a MarkdownAnalyzer instance, that converts some of its output to readily processing formats,
    and as a base to add more that is needed by the program, that MarkdownAnalysis does not provide.
    """

    def __init__(self, path):
        """
        Holds

        (MarkdownAnalyzer) instance
        (Path) string Path of the .md
        """
        self.analyzer = mrkdwn_analysis.MarkdownAnalyzer(path)
        self.md_path = path

    def get_headers(self) -> dict[str, list[str]]:
        # Utilize the identify_headers() to extract the information of all headers
        return self.analyzer.identify_headers()

    def get_header_hierarchy(self) -> list:
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
