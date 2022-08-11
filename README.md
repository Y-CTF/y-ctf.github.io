# Y-CTF

This project contains the website for the Y-CTF club. 

## Contribute

### Add an event


### Add a post


### Writeups


### Markdown syntax

Kramdown is used to render the markdown files to HTML.

Here is a quick reference guide for Kramdown:
- https://kramdown.gettalong.org/quickref.html

Some useful syntaxes you can use in the Markdown files:

#### Add an ID to an element 

Syntax: `<element>{:#<id>}`

Example:

```markdown
...


# À propos du club
{:#a-propos}

...
```
#### Add HTML attribute

Syntax: `<element>{:<att>="<value>`}

For example, you can add classes to an image in order to apply CSS on it:

```markdown
...

![](assets/img/logos/logo-dark.png){:class="pres-image center"}

...
```

#### Include HTML

Syntax: `{% <name of the template in _includes directory %}`

Example:
```markdown
{% include separator.html %}
```

More information here: [https://jekyllrb.com/docs/includes/]()



## How to run the site locally

Useful link: [GitHub pages tutorial](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll )

### Install requirements
1. Install prerequisites from [this](https://jekyllrb.com/docs/installation/#requirements) page (example for Ubuntu):

```bash
sudo apt install ruby-full build-essential zlib1g-dev
```

2. Export these env. variables in order to run gem without sudo (for example in .bashrc, .zshrc)

```
export GEM_HOME="$HOME/gems"
export PATH="$HOME/gems/bin:$PATH"
```

3. Reload the terminal to apply the new environment variables
4. Install Jekyll and Bundler

```bash
gem install jekyll bundler
```

5. Install the gem dependencies

```bash
bundle install
```

### Run a local server

When you have installed the prerequisites, you can simply run this command to serve the jekyll site:

```bash
bundle exec jekyll serve
```

You can add the `--watch` flag to update the site automatically when you modify the content:

```bash
bundle exec jekyll serve --watch
```

By default, the server will be available at `http://localhost:4000`