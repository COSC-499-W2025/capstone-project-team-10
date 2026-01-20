import mrkdwn_analysis
from src.fas.fas_text_analysis import TextSummary
from src.fas.fas_extra_data import _extract_text_skills


class Markdown:

    def __init__(self, path):
        self.analyzer = mrkdwn_analysis.MarkdownAnalyzer(path)
        self.md_path = path

    def analyze_markdown(path):
        md = Markdown(path)
        return {
                    "header_hierarchy": md.get_header(),
                    "word_count": md.get_word_counts(),
                    "code_blocks": md.get_code_blocks(),
                    "paragraphs": md.get_paragraphs(),
                }

    def get_headers(self) -> dict[str, list[str]]:
        # Utilize the identify_headers() to extract the information of all headers
        return self.analyzer.identify_headers()

    def get_header(self) -> list[str]:
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

        # Return only top-level header titles as strings
        return [item["title"] for item in root]

    def get_word_counts(self) -> int:
        # Output: (int) number of word counts within the .md
        return self.analyzer.count_words()

    def get_code_blocks(self) -> set[str]:
        # Returns unique code languages used in markdown file
        code_dict = self.analyzer.identify_code_blocks()
        languages = set()
    
        if isinstance(code_dict, dict):
            code_blocks = code_dict.get('Code block', [])
        
            if isinstance(code_blocks, list):
                for block in code_blocks:
                    if isinstance(block, dict) and 'language' in block:
                        lang = block['language']
                        if lang:
                            languages.add(lang)
    
        return languages

    def get_paragraphs(self):
        # Returns key skills present in the markdown file from the dict
        paragraphs_dict = self.analyzer.identify_paragraphs()

        if isinstance(paragraphs_dict, dict):
            text = paragraphs_dict.get('Paragraph', '') or \
                   paragraphs_dict.get('paragraphs', '')

            if isinstance(text, list):
                text = ' '.join(str(p) for p in text)
            else:
                text = str(text) if text else ''
        else:
            text = str(paragraphs_dict) if paragraphs_dict else ''
        
        analyzer = TextSummary(text) if text.strip() else None
        if analyzer:
            output = analyzer.generate_text_analysis_data(10, 3)
            output = {
                'complexity': output.get('complexity', ''),
                'depth': output.get('depth', ''),
                'structure': output.get('structure', ''),
                'sentiment_insight': output.get('sentiment_insight', '')
            }
            output = _extract_text_skills(output)
            return output
        return None