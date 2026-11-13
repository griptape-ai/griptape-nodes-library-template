---
description: Where each kind of doc page goes in a library, and how pages are matched to nodes.
when_to_use: Read this when you add docs to your own library.
---

# Writing docs for your own library

Docs live in a `docs/` folder next to the library's JSON file. The engine reads them from the installed library, so they work offline and always match the version you're running.

## What goes where

| Folder | One page for each | Name the page after |
| --- | --- | --- |
| `docs/nodes/` | node in `nodes` | the node's class name (`CreateName.md`), or its display name written with underscores (`set_age.md`) |
| `docs/workflow_nodes/` | node in `workflow_nodes` | the node type (`IntroduceYourself.md`) |
| `docs/workflows/` | template in `workflows` | the template's file name without `.py` |
| `docs/tools/` | MCP tool the library offers agents | the tool's request type (`TranslateToPigLatinRequest.md`) |

Pages can sit in subfolders. This library groups its control nodes in `docs/nodes/control/`, and leaves `CreateName.md` at the top. The folders are your choice. Only the filename matters.

Everything else under `docs/` is about the library as a whole, like this guide. Name the folders however you like. `index.md` is the library's overview page. Without one, the engine shows the README.

## Frontmatter

Every page can start with a few optional fields:

```yaml
---
title: Shown instead of the node's display name
description: One or two sentences on what the page covers.
when_to_use: When to pick this node over another.
---
```

A node page without a title uses the node's display name. A library page without one uses its first heading.

## Pages you don't write

A node with no page still gets one, built from its description and the table of its parameters. Of this library's nodes, only a few have pages written by hand. Open the strict-mode nodes to see the built page.

When a tooltip isn't enough, add a `## Parameters` section to the page with a `###` heading per parameter. Each explanation is shown with that parameter in the table. [Create a Name](../nodes/CreateName.md) does this.

## MCP tools

A library can hand agents tools of its own. This one offers `TranslateToPigLatinRequest`, defined in `example_nodes_template/example_tools.py`. The Docs panel lists it under **Agent MCP tools**.

Without a page, a tool is documented by the request's docstring, the descriptions of its fields, and whether it only reads. Write those for an agent choosing between tools. When you have more to say, add a page in `docs/tools/`. [Translate to pig latin](../tools/TranslateToPigLatinRequest.md) shows one, and its `title` and `description` replace the generated ones.

## Skills for agents

An agent that builds workflows with your library reads skills in `docs/.agents/skills/`. One folder per skill, each with a `SKILL.md`. This library ships [build-an-introduction](../.agents/skills/build-an-introduction/SKILL.md) as an example. Skills for people or agents working on the library's code don't go here. Keep those in `.agents/skills/` at the top of the repo, and developer docs in `dev/docs/`, so they never show up in the editor.
