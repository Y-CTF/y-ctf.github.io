<p align="center">
    <img src="assets/banner-gray.png#gh-light-mode-only" alt="Logo" height="250">
    <img src="assets/banner-white.png#gh-dark-mode-only" alt="Logo" height="250">
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

Writeups are stored in the `content/writeups/` directory as a **git submodule** pointing to the [writeups repository](https://github.com/y-ctf/writeups).

For contributing writeups, formatting guidelines, and detailed documentation, see the [writeups repository README](https://github.com/y-ctf/writeups/blob/main/README.md).

### Events

Events are stored in the `content/data/events.toml` file and displayed on the events page at `content/pages/events.md`.

Example event entry:

```toml
[[events]]
title = { en = "Event title in English", fr = "Titre de l'event en français" }
description = { en = "Brief description of the event", fr = "Description brève de l'event" }
start_date = "2025-10-15T18:00:00+01:00"             # ISO 8601 format
end_date = "2025-10-15T20:00:00+01:00"               # ISO 8601 format
location = "Physical/Virtual location"
type = "competition"                                 # competition, meeting, conference, training, etc.
url = "https://example.com"                          # Optional external link, shown as "learn more"
registration_deadline = "2025-10-14T23:59:59+01:00"  # Optional deadline
```

Events are automatically imported from ICS calendar files using the import script (see the "Importing Events from ICS Calendar" section below).

## Development

1. Clone the repository with submodules

```bash
git clone --recurse-submodules https://github.com/y-ctf/y-ctf.github.io.git
cd y-ctf.github.io
```

Or if you've already cloned without submodules:

```bash
git submodule update --init --recursive
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

A python script is provided to import writeups from a specific past CTF directly into the writeups submodule.

<details open>
<summary>With <a href="https://docs.astral.sh/uv/getting-started/installation/"><code>uv</code></a></summary>
<p></p>

```bash
uv run scripts/import.py ctf -c "<ctf-name>" -a "Bearer <token>" -o "content/writeups/<ctf-name>"
```

</details>
<details>
<summary>With <code>python</code></summary>
<p></p>

```bash
pip install requests tomlkit rich python_slugify
python scripts/import.py ctf -c "<ctf-name>" -a "Bearer <token>" -o "content/writeups/<ctf-name>"
```

</details>

### After importing

1. Commit and push changes in the writeups submodule:
   ```bash
   cd content/writeups
   git add .
   git commit -m "add writeups for <ctf-name>"
   git push
   ```

2. Update the submodule reference in the main repository:
   ```bash
   cd ../..
   git add content/writeups
   git commit -m "update writeups submodule"
   git push
   ```

## Importing Events from ICS Calendar

The same python script can also be used to import events from an ICS calendar file or URL and add them to the [`events.toml`](content/data/events.toml) file.

To import events directly from CTFNote, you'll need the ICS URL and the iCalendar secret key.

<details>
<summary>How to retrieve the iCalendar URL</summary>
<p></p>

![](assets/icalendar-ics.png)

</details>

<details open>
<summary>With <a href="https://docs.astral.sh/uv/getting-started/installation/"><code>uv</code></a></summary>
<p></p>

```bash
# from a local ICS file
uv run scripts/import.py ics -i "path/to/calendar.ics"

# from an URL
uv run scripts/import.py ics -i "https://yctf.ch/calendar.ics?key=<CALENDAR_KEY>" --event-type "competition"
```

</details>
<details>
<summary>With <code>python</code></summary>
<p></p>

```bash
pip install requests tomlkit rich icalendar

# from a local ICS file
python scripts/import.py ics -i "path/to/calendar.ics"

# from a URL
python scripts/import.py ics -i "https://yctf.ch/calendar.ics?key=<CALENDAR_KEY>" --event-type "competition"
```

</details>