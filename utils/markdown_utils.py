# Markdown utilities for Gut Health Management App

# Import markdown library (will try both)
try:
    import markdown2
    MARKDOWN_PROCESSOR = 'markdown2'
except ImportError:
    try:
        import markdown
        MARKDOWN_PROCESSOR = 'markdown'
    except ImportError:
        MARKDOWN_PROCESSOR = None


def parse_markdown(md_content):
    """Convert markdown to HTML"""
    if MARKDOWN_PROCESSOR == 'markdown2':
        return markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks', 'header-ids', 'task-list'])
    elif MARKDOWN_PROCESSOR == 'markdown':
        return markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc', 'nl2br'])
    else:
        # Fallback: basic HTML escaping and newline conversion
        import html
        return html.escape(md_content).replace('\n', '<br>')


def extract_title_from_markdown(md_content):
    """Extract title from first H1 in markdown"""
    lines = md_content.split('\n')
    for line in lines:
        # Check for # Title format
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
        # Check for Title\n=== format
        if line.strip() and len(lines) > lines.index(line) + 1:
            next_line = lines[lines.index(line) + 1]
            if next_line.strip().startswith('==='):
                return line.strip()
    return "Untitled Chapter"
