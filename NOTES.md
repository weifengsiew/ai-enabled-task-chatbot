## Stage 0

### Understanding src/bao/cli.py

After opening src/bao/cli.py, I see that the main function calls the farewell function. 

### Understanding pyproject.toml

`pyproject.toml` is the main configuration file for a modern Python project. It tells Python tooling things like what your project is called, which Python versions it supports, how it should be installed, what command-line programs it exposes, and how it should be built.

Conceptually, your `pyproject.toml` is doing three jobs:

- describing the Python project
- defining the `bao` CLI command
- telling tools like `uv` how to build/install it

For your file:

```toml
[project]
name = "bao"
version = "0.1.0"
requires-python = ">=3.13,<3.14"
```

this defines the package metadata. Your project is named `bao`, its version is `0.1.0`, and it requires Python 3.13 specifically.

```toml
[project.scripts]
bao = "bao.cli:main"
```

This defines a command-line entry point. After the project is installed, running:

```bash
bao
```

calls:

```python
bao.cli.main()
```

And:

```toml
[build-system]
requires = ["uv_build>=0.11.3,<0.12.0"]
build-backend = "uv_build"
```

tells packaging tools how to build your project. In this case, you're using `uv_build` as the build backend.

### Stage 0 Takeaways

What happens between entering uv run bao and seeing the first line?

uv run bao calls bao.cli.main(), which is the function main() in src/bao/cli.py

Which function would you change if the farewell needed different wording?

I would change the main() function. 

Why is running the command yourself still useful after an agent has run it?


