# Markdown Formatting Guide

The Education editor supports full markdown formatting for creating rich, professional content.

---

## Text Formatting

```markdown
**Bold text**
*Italic text*
***Bold and italic***
~~Strikethrough~~
`Inline code`
<u>Underline</u>  (use HTML - standard markdown doesn't support underline)
```

---

## Headers

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

---

## Lists

```markdown
Unordered lists:
- Item 1
- Item 2
    - Nested item (press Tab to indent)
        - Deeply nested item

Ordered lists:
1. First item
2. Second item
3. Third item
```

---

## Links

Links automatically open in a new tab.

```markdown
[Link text](https://example.com)
[Monash FODMAP](https://www.monashfodmap.com/)
```

---

## Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

*Tables display with styled headers (dark green with gold text) and zebra-striped rows.*

---

## Images

```markdown
![Alt text](image-url.jpg)
```

*Images auto-resize and display with rounded corners.*

---

## Code Blocks

````markdown
```python
def example():
    return "Hello, World!"
```
````

---

## Blockquotes

```markdown
> This is a quoted text
> It can span multiple lines
```

---

## Horizontal Rules

```markdown
---
or
***
```

---

## Tab Indentation

- Press **Tab** to indent (adds 4 spaces)
- Press **Shift+Tab** to remove indentation
- Great for creating nested lists and indented content

---

## Preview Feature

- Switch between "Edit Markdown" and "Preview" tabs
- See exactly how your content will look before saving
- External links are automatically configured to open in new browser tabs
