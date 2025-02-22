# Valyu Get Context Tool

This tool connects your AI agents to proprietary data sources and the web using the Valyu API. It allows you to fetch context based on a query, with options to limit the number of results and set a maximum price.

## Usage

To use this tool, you need to provide a JSON object with the following properties:

* `query`: The search query to fetch context for.
* `search_type`: The type of search to perform, defaults to 'all' which is proprietary data sources and the web, or 'proprietary' which is proprietary data sources only.
* `max_num_results`: The maximum number of results to return. Defaults to 10.
* `max_price`: The maximum price to consider for the results. Defaults to 10.

Example input:
```json
{
  "query": "example query",
  "search_type": "all",
  "max_num_results": 5,
  "max_price": 5
}
```

The tool will output the fetched context in JSON format.

## Implementation

This tool is implemented in Python using the Valyu API. It utilizes the `pydantic` library for model validation and the `valyu` library for interacting with the Valyu API.

The tool's structure follows the standard for sandboxed tools, as described in [Using Sandboxed Tools](https://github.com/vessl-ai/hyperpocket/tree/main/docs/hyperpocket/tools/using-sandboxed-tools.md). The `pocket.json` file defines the tool's metadata, including its name, description, input schema, and execution entrypoints.

The `schema.json` file defines the input schema for the tool, specifying the properties and their types. The `__main__.py` file contains the implementation of the tool, including the model definition, the logic for fetching context, and the main entrypoint for execution.

## Dependencies

This tool depends on the following packages:

* `pydantic`
* `valyu`

These dependencies are specified in the `pyproject.toml` file and can be installed using a package manager like pip.
