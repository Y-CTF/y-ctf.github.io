<p align="center">
    <img src="static/images/banner_light.png#gh-light-mode-only" alt="Logo" height="200">
    <img src="static/images/banner_dark.png#gh-dark-mode-only" alt="Logo" height="200">
</p>

--- 

Source code of the [yctf.ch](https://yctf.ch) website.

## Writing Content

The file structure is as follows:

```
content/
├── pages/
│   └── ...
└── writeups/
    ├── <ctf-name>/
    │   └── <challenge-name>/
    │       ├── index.md
    │       └── files/
    │           ├── <files>
    │           └── ...
    └── ...
```

### Pages

Mostly static pages like the home page, about page, etc. are stored in the `content/pages/` directory.

### Writeups

Writeups are stored in the `content/writeups/` directory. Each CTF has its own directory, and each challenge has its own directory within that. The `index.md` file contains the writeup, and any files associated with the challenge are stored in the `files/` directory.

#### Frontmatter

The frontmatter of a writeup is in TOML format and looks like this:

```toml
+++
title = "Challenge Name"
date = 2021-01-01
description = "Description of the challenge" # Optional
authors = ["Author 1", "Author 2"] # Optional

[taxonomies]
categories = ["pwn"]
+++
```

### Markdown

The content is rendered using a fork of [Zola](https://github.com/cestef/zola). It supports the standard markdown syntax, as well as some custom stuff:

- [`typst`](https://typst.app) math rendering

```markdown
$$
lim_(x->oo) (1 + 1/x)^x = e
$$
```

- Obsdian-like callouts

```markdown
> [!NOTE]
> This is a note
```

- Code block injection

~~~markdown
```python include=files/solution.py
```
~~~

- Copy button

~~~markdown
```python copy
print("Hello, world!")
```
~~~

## Development

1. Clone the repository

```bash
git clone https://github.com/yctf/site.git
cd site
```

2. Install Zola ([`brew`](https://brew.sh) or [`cargo`](https://rustup.rs))

```bash
brew install cestef/tap/zola
# or with cargo
cargo install --git https://github.com/cestef/zola
```

<small>You can also download a pre-built binary from the [releases page](https://github.com/cestef/zola/releases).</small>

3. Install dependencies ([`pnpm`](https://pnpm.io))

```bash
pnpm install
```

4. Start the development server

```bash
pnpm dev
```

## Importing Writeups from [CTFNote](https://note.yctf.ch)

A python script is provided to import writeups from a specific past CTF. It will download the writeups and format them into the correct structure.

### With [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv run scripts/import.py -c "ctf-name" -a "Bearer <token>" -o "content/writeups/<ctf-name>"
```

### With `python`

```bash
pip install requests tomlkit rich python_slugify
python scripts/import.py -c "ctf-name" -a "Bearer <token>" -o "content/writeups/<ctf-name>"
```