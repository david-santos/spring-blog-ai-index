#!/usr/bin/env python3
"""Build an index.html of Spring Engineering posts related to Spring AI."""

import re
import sys
import urllib.request
from html import unescape, escape

BASE = "https://spring.io"
CATEGORY_PATH = "/blog/category/engineering/"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read().decode("utf-8", "ignore")


def strip_tags(html):
    # Remove scripts/styles first to avoid junk text
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_articles(html):
    # Capture each blog post article block
    blocks = re.findall(r"<article class=\"blog-post[\s\S]*?</article>", html)
    articles = []
    for block in blocks:
        title_match = re.search(
            r"<h1[^>]*>\s*<a href=\"(/blog/[^\"]+)\">([^<]+)</a>",
            block,
        )
        if not title_match:
            continue

        href, title = title_match.groups()
        if href == "/blog" or not re.search(r"/blog/\d{4}/", href):
            continue

        content_match = re.search(
            r"<div class=\"content markdown\">([\s\S]*?)</div>",
            block,
        )
        excerpt_html = content_match.group(1) if content_match else ""
        excerpt_text = strip_tags(excerpt_html)

        date_match = re.search(r"\b([A-Z][a-z]+ \d{1,2}, \d{4})\b", block)
        date_text = date_match.group(1) if date_match else ""

        articles.append({
            "title": re.sub(r"\s+", " ", title).strip(),
            "url": BASE + href,
            "excerpt": excerpt_text,
            "date": date_text,
        })

    return articles


def build_index(output_path="index.html"):
    page = 1
    seen_urls = set()
    spring_ai_posts = []  # newest -> oldest, based on crawl order

    while True:
        if page == 1:
            url = f"{BASE}{CATEGORY_PATH}"
        else:
            url = f"{BASE}{CATEGORY_PATH}page-{page}/"

        try:
            html = fetch(url)
        except Exception:
            break

        articles = extract_articles(html)
        if not articles:
            break

        new_count = 0
        for article in articles:
            if article["url"] in seen_urls:
                continue
            seen_urls.add(article["url"])
            new_count += 1

            if re.search(r"\bSpring AI\b", article["title"], re.IGNORECASE):
                spring_ai_posts.append({
                    "title": article["title"],
                    "url": article["url"],
                    "excerpt": article["excerpt"],
                    "date": article["date"],
                    "found_on": url,
                })

        if new_count == 0:
            break

        page += 1
        if page > 400:
            break

    # Newest to oldest is the crawl order already

    html_out = []
    html_out.append("<!DOCTYPE html>")
    html_out.append('<html lang="en">')
    html_out.append("<head>")
    html_out.append("  <meta charset=\"utf-8\">")
    html_out.append("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    html_out.append("  <title>Spring Engineering: Spring AI Posts</title>")
    html_out.append("  <style>")
    html_out.append("    :root { color-scheme: light; }")
    html_out.append("    body { font-family: Georgia, 'Times New Roman', serif; margin: 40px; line-height: 1.6; }")
    html_out.append("    h1 { font-size: 28px; margin-bottom: 8px; }")
    html_out.append("    p { margin-top: 0; color: #555; }")
    html_out.append("    ul { padding-left: 18px; }")
    html_out.append("    li { margin: 12px 0; }")
    html_out.append("    a { color: #1f5f2a; text-decoration: none; }")
    html_out.append("    a:hover { text-decoration: underline; }")
    html_out.append("    .meta { color: #666; font-size: 0.9em; }")
    html_out.append("    .excerpt { color: #333; }")
    html_out.append("  </style>")
    html_out.append("</head>")
    html_out.append("<body>")
    html_out.append("  <h1>Spring Engineering: Spring AI Posts</h1>")
    html_out.append("  <p>Indexed from https://spring.io/blog/category/engineering. Total: %d</p>" % len(spring_ai_posts))
    html_out.append("  <ul>")
    for post in spring_ai_posts:
        title = escape(post["title"])
        url = escape(post["url"], quote=True)
        found_on = escape(post["found_on"], quote=True)
        excerpt = escape(post["excerpt"])
        date_text = escape(post["date"])
        html_out.append("    <li>")
        html_out.append("      <div><a href=\"%s\">%s</a></div>" % (url, title))
        meta_bits = []
        if date_text:
            meta_bits.append("Date: %s" % date_text)
        meta_bits.append("Found on: <a href=\"%s\">%s</a>" % (found_on, found_on))
        html_out.append("      <div class=\"meta\">%s</div>" % " | ".join(meta_bits))
        if excerpt:
            html_out.append("      <div class=\"excerpt\">%s</div>" % excerpt)
        html_out.append("    </li>")
    html_out.append("  </ul>")
    html_out.append("</body>")
    html_out.append("</html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_out))

    print("pages scanned:", page)
    print("spring ai posts:", len(spring_ai_posts))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    build_index(out)
