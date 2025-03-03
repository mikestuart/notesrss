from bs4 import BeautifulSoup

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    en_note = soup.find("en-note")
    if en_note:
        soup = BeautifulSoup(en_note.decode_contents(), "html.parser")

    # remove <script>, <style>, etc.
    for bad in soup(["script", "style", "meta", "link"]):
        bad.decompose()

    # strip style/class/id/etc.
    for tag in soup.find_all(True):
        for unwanted_attr in ["id", "class", "style", "rev", "onclick"]:
            if unwanted_attr in tag.attrs:
                del tag.attrs[unwanted_attr]

    # convert <div> → <p> if only inline elements
    block_level_tags = {
        "article","aside","blockquote","div","dl","fieldset","figcaption","figure",
        "footer","form","h1","h2","h3","h4","h5","h6","header","hr","li",
        "main","nav","noscript","ol","p","pre","section","table","td","th","tr","ul"
    }
    for div in soup.find_all("div"):
        has_block_child = False
        for child in div.descendants:
            if child is div:
                continue
            if child.name in block_level_tags:
                has_block_child = True
                break
        if not has_block_child:
            div.name = "p"

    # remove empty <p> or headings if they only contain <br> or whitespace
    def is_empty_block(tag):
        if tag.get_text(strip=True):
            return False
        for child in tag.children:
            if child.name and child.name != "br":
                return False
        return True

    for block_tag in soup.find_all(["p", "h1","h2","h3","h4","h5","h6"]):
        if is_empty_block(block_tag):
            block_tag.decompose()

    # === Return multi-line pretty-printed HTML ===
    return soup.prettify(formatter="html")

def wrap_html_document(title, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
{content}
</body>
</html>"""
