# Spring Engineering Spring AI Index

This script crawls the Spring Engineering blog category pages and builds an `index.html` listing all posts with "Spring AI" in the title. It records the page where the post was found and includes the excerpt shown on the category page.

## Requirements

- Python 3
- Network access to `spring.io`

## Usage

From `/Users/davidsantos/Downloads`:

```sh
python3 build_spring_ai_index.py
```

This writes `index.html` in the same directory.

Optional output path:

```sh
python3 build_spring_ai_index.py /path/to/index.html
```

## Notes

- Pagination is crawled via `/blog/category/engineering/page-N/`.
- Results are ordered newest to oldest (crawl order).
- The excerpt is taken from the small body text shown on the category pages.
