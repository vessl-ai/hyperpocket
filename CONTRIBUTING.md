# Contributing

Thank you for your interest in contributing to Hyperpocket! We welcome contributions in any form, whether code, documentation, tools or simply spreading the word about the project.

*This guide was heavily inspired by (🤗 Transformers guide to contributing)[https://github.com/huggingface/transformers/blob/main/CONTRIBUTING.md].*

## How You Can Contribute

We value any and all contributions, including:

- **Submitting Issues**  
 If you encounter bugs or problems, let us know! Apparent, detailed issues help us pinpoint and fix problems quickly.

- **Opening Pull Requests (PRs)**  
 You can fix bugs, add new features, contribute tools or integrations, or enhance our examples. We appreciate both major and minor improvements.

- **Improving Documentation**  
 Good documentation is vital. Your help is appreciated, whether it's fixing typos, clarifying existing content, or adding brand-new sections.

## Submitting issues

### Reporting bugs

When reporting a bug, please include the following details:

- Your running environment.
- A code snippet or steps to reproduce the issue.
- The **error message** and full stack trace.

### Requesting features

When submitting a feature request, please include:

1. A clear and detailed **feature description**.
2. The **use case** or problem the feature would address.
3. The **expected behavior** or functionality.

Well-documented issues help us address them more efficiently!

## Creating pull requests

### Setup instructions

Follow these steps to set up your development environment:

1. Ensure you have **Python 3.10** or higher installed.
2. Fork the repository on GitHub.
3. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (our dependency management tool).
4. Clone your forked repository:
```bash
   git clone https://github.com/<your-username>/hyperpocket.git
   cd hyperpocket
```
5. Install the required dependencies for the package you want to work on:
```bash
   uv sync --frozen --dev
```

### Workflow guidelines

1. Create a new branch from main with a descriptive name, such as `feature/add-auth-provider` or `bugfix/fix-error-handling`:
```bash
   git checkout -b my-new-branch
```
2. Make your changes, ensuring your code is well-documented and follows our standards.
3. Run tests to ensure everything works as expected:
```bash
   uv run pytest
```
4. Lint and format your code:
```bash
   uv run ruff check .
   uv run ruff format .
```
5. Commit your changes with a clear message that explains what you did.
6. Push your branch and open a pull request to the `main` branch.
7. Discuss and revise as needed based on feedback from maintainers or the community.


### Code style

We adhere to strict coding standards to maintain consistency and quality across the codebase. We use [ruff](https://astral.sh/ruff) for linting and formatting, configured in `pyproject.toml`.

To keep your contributions consistent with our style, we recommend installing pre-commit hooks:
```bash
pre-commit install
```

These hooks automatically run checks whenever you commit, helping you quickly catch formatting or style issues.


## Documentation

We value clear and accurate documentation. If you'd like to contribute to our documentation, such as adding new content, fixing typos or inaccuracies, or enhancing clarity, feel free to submit issues or open pull requests, as we mentioned above.


## Code of Conduct

We expect all contributors to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to uphold a respectful and inclusive community.


## License

By contributing to Hyperpocket, you agree that your contributions will be licensed under the MIT License.

Thank you for helping make Hyperpocket awesome! 🎉
