---
name: node-errors
description: Write a Griptape Nodes node's error handling - helpful error messages, NodeError with fields/response/links, a missing API key, validation errors, and routing failures through the Failed output. Use whenever you add or change a raise, a validate_before_node_run exception, or a _set_status_results(was_successful=False) call.
---

# Node Error Handling

The editor shows a failed node's name and message. A `NodeError` can also carry `fields`, `response`,
and `links`, which the editor shows under **More info**.

Reference: the engine's `docs/development/custom_nodes/example_node_error_node.py`.

## Writing the message

A good message lets an artist fix the problem without asking anyone. Include:

- **Which parameter**, using the label the UI shows.
- **What's wrong with it**, including the value when it helps.
- **What's allowed**, such as a range or the supported formats.
- **What to do next.**

| Instead of | Write |
| --- | --- |
| "Invalid input." | "'Width' must be between 256 and 2048. It's set to 4000." |
| "Could not read the source image." | "Could not read the image connected to 'Input Image'. Connect a PNG or JPEG." |
| "No model ID provided" | "No model is selected. Choose one in 'Model' and run the node again." |
| "Request failed: 429" | "The provider is rate-limiting requests. Wait a minute and run the node again." |

Don't start with the node's name; the editor shows it. Don't paste a response or `repr()` into the
message; attach it instead.

**Link to the fix when a page explains it**: the provider's docs for a limit or content policy, a
supported-formats page, or a place in the editor such as `#settings-secrets?filter=KEY`. Only link
pages that exist. A link to a generic home page doesn't help.

## Raise NodeError

Raise `NodeError` for the errors your nodes report. It takes just a message:

```python
from griptape_nodes.exe_types.core_types import NodeError, NodeErrorLink

raise NodeError(
    "The prompt contains blocked words. Rephrase it and try again.",
    links=[NodeErrorLink(label="Content policy", url="https://example.com/content-policy")],
)
```

You can attach any of three optional parts:

- `fields`: labelled values a user may quote to support, such as a status code or request ID.
- `links`: up to three pages that explain the fix.
- `response`: the provider's response body, under 16 KB. Remove base64 data first.

```python
raise NodeError(
    "The prompt contains blocked words. Rephrase it and try again.",
    fields={"status_code": 400, "request_id": "req_8f2c41d0"},
    links=[NodeErrorLink(label="Content policy", url="https://example.com/content-policy")],
    response={"error": {"code": "content_policy", "message": "The prompt contains blocked words."}},
)
```

When re-raising a caught exception, add `from e`. Use the provider's own message as the message, and
put the status code and request ID in `fields`.

An SDK exception's `str()` or `.message` often holds the whole response. OpenAI's `APIStatusError`
message is `Error code: 401 - {'error': {...}}`. Read the provider's message from the parsed body
(`e.body`) instead, and attach that body as `response`.

**Don't re-wrap** an exception just to add a prefix (`raise RuntimeError(f"Failed: {e}") from e`).
It adds nothing and replaces the type in logs and tracebacks. Let it propagate.

## Missing API key

Check before the node runs, and return one exception per problem so the editor lists each on its own
line:

```python
from urllib.parse import quote

def validate_before_node_run(self) -> list[Exception] | None:
    if self._api_key_is_set():
        return None
    return [
        NodeError(
            f"{API_KEY_NAME} is not set. Add it in Settings → API Keys & Secrets, then run the node again.",
            links=[NodeErrorLink(label="Add the API key", url=f"#settings-secrets?filter={quote(API_KEY_NAME)}")],
        )
    ]
```

A `#` link opens a place in the editor. URL-encode any values in its query.

## Every failure must reach the editor

In a `SuccessFailureNode`, route every failure through `_handle_failure_exception`. It follows
**Failed** if that's wired, and raises otherwise. Setting the status and returning is a silent
failure: with **Failed** unwired, nothing shows up.

```python
error = NodeError("Connect a file to 'Source'.")
self._set_status_results(was_successful=False, result_details=str(error))
self._handle_failure_exception(error)
return
```

- Call `_set_status_results` before `_handle_failure_exception`, and `return` after it.
- Don't `raise` again after it, or a wired **Failed** output can't catch the failure.
- Nodes without a **Failed** output just raise.
- Never raise from `after_value_set`, button callbacks, or previews. Only from `process`.

## Testing

```python
def test_raises_when_failed_is_unwired(node):
    node._has_outgoing_connections = lambda _param: False
    with pytest.raises(NodeError, match="Connect a file"):
        node.process()

def test_follows_failed_when_wired(node):
    node._has_outgoing_connections = lambda _param: True
    node.process()
    assert node.parameter_output_values["was_successful"] is False
```

For a `NodeError`, also assert its attachments: `assert raised.value.fields == {...}`.
