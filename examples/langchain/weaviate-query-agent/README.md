# Weaviate Query Agent

## How to run this code

You need docker to be installed in your local environment.

```shell
pip install "hyperpocket[standard]" hyperpocket-langchain langchain_openai
python weaviate_query_agent/agent.py
```

or simply,

```shell
uv run python weaviate_query_agent/agent.py
```

### Testing your code
```shell
export WCD_URL="https://..."
export OPENAI_API_KEY="sk_..."
python weaviate_query_agent/agent.py
```

Then, try ask something about weaviate:

```
Hello, this is langchain weaviate agent.
user(q to quit) : Create a weaviate collection moon.


> Entering new AgentExecutor chain...

Invoking: `weaviate_create_collection` with `{'name': 'moon'}`


User needs to authenticate using the following URL: https://...

The tool execution interrupted. Please talk to me to resume. It looks like you need to authenticate to proceed with creating the collection. Please visit the following URL to authenticate:

[Authenticate Here](https://...)

Once you've authenticated, let me know, and we can continue with creating the collection.

> Finished chain.
weaviate agent :  It looks like you need to authenticate to proceed with creating the collection. Please visit the following URL to authenticate:

[Authenticate Here](https://localhost:8001/proxy/auth/token?redirect_uri=https%3A%2F%2Flocalhost%3A8001%2Fproxy%2Fauth%2Fweaviate%2Ftoken%2Fcallback&state=464e9120-59c0-42cb-a217-4c76dd4e5976)

Once you've authenticated, let me know, and we can continue with creating the collection.

user(q to quit) : I'm done.


> Entering new AgentExecutor chain...

Invoking: `weaviate_create_collection` with `{'name': 'moon'}`


Collection moon created successfully.
The collection "moon" has been created successfully in Weaviate. If you have any more tasks or data to import, feel free to ask!

> Finished chain.
weaviate agent :  The collection "moon" has been created successfully in Weaviate. If you have any more tasks or data to import, feel free to ask!

user(q to quit) : Moon is a developer in a startup VESSL AI, and is legendary. Put this info into the collection moon.  


> Entering new AgentExecutor chain...

Invoking: `weaviate_import_data` with `{'collection_name': 'moon', 'data_row': '{"name": "Moon", "description": "Moon is a developer in a startup VESSL AI, and is legendary."}'}`


success
The information about Moon has been successfully added to the "moon" collection in Weaviate. If you need to add more details or have other tasks, feel free to let me know!

> Finished chain.
weaviate agent :  The information about Moon has been successfully added to the "moon" collection in Weaviate. If you need to add more details or have other tasks, feel free to let me know!

user(q to quit) : Who is legendary?


> Entering new AgentExecutor chain...

Invoking: `query_near_text` with `{'collection_name': 'moon', 'query': 'legendary', 'limit': 1}`


[
  {
    "description": "Moon is a developer in a startup VESSL AI, and is legendary.",
    "name": "Moon"
  }
]
Moon is described as legendary.

> Finished chain.
weaviate agent :  Moon is described as legendary.

user(q to quit) : Read all objects in the collection moon.


> Entering new AgentExecutor chain...

Invoking: `weaviate_read_all_objects` with `{'collection_name': 'moon', 'include_vector': False}`


[
  {
    "id": "0xdeadbeef",
    "properties": {
      "description": "Moon is a developer in a startup VESSL AI, and is legendary.",
      "name": "Moon"
    },
    "vector": {}
  }
]
The collection "moon" contains the following object:

- **Name**: Moon
- **Description**: Moon is a developer in a startup VESSL AI, and is legendary.

If you need further details or assistance, let me know!

> Finished chain.
weaviate agent :  The collection "moon" contains the following object:

- **Name**: Moon
- **Description**: Moon is a developer in a startup VESSL AI, and is legendary.

If you need further details or assistance, let me know!

user(q to quit) : What's the object with id 0xdeadbeef?


> Entering new AgentExecutor chain...

Invoking: `weaviate_read_object_by_id` with `{'collection_name': 'moon', 'object_id': '8e657999-556d-4f58-a645-d3b95989b154'}`


{
  "id": "0xdeadbeef",
  "properties": {
    "description": "Moon is a developer in a startup VESSL AI, and is legendary.",
    "name": "Moon"
  },
  "vector": {}
}
The object with ID `0xdeadbeef` in the "moon" collection has the following properties:

- **Name**: Moon
- **Description**: Moon is a developer in a startup VESSL AI, and is legendary.

If you have more questions or need further assistance, feel free to ask!
```
