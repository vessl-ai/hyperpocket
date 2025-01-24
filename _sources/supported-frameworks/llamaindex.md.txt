# LlamaIndex

**LlamaIndex** allows language models to interact with structured data. Hyperpocket tools can be integrated for retrieving and managing data dynamically.

**Example: Using LlamaIndex with Hyperpocket Tools**

```python
from llama_index import SimpleKeywordTableIndex
from hyperpocket.tool import from_git

# Load a tool
tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message")

# Create an index
index = SimpleKeywordTableIndex()
index.insert("tool", tool)

# Query the index
results = index.query("Fetch the last 5 Slack messages from the general channel.")
print(results)
```