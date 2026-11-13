---
title: Translate to pig latin
description: Turns a short piece of English text into pig latin, so you can preview it before using a node.
when_to_use: Use this to check how a phrase translates. To translate inside a workflow, use the Convert to Pig Latin node.
---

An agent that is building a workflow can ask for a translation before it wires anything up. The tool never changes the workflow.

## Example

Ask for `hello world` and you get back `ellohay orldway`. A word that starts with a vowel gets `way` on the end, so `apple` becomes `appleway`.

## What comes back

The tool returns the translated text. If the text is empty, it fails and says so.

## Related

[Convert to Pig Latin](../nodes/control/ConvertToPigLatin.md) does the same inside a workflow.
