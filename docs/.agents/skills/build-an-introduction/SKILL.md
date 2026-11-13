---
name: build-an-introduction
description: Build a short introduction from a name and an age with the Example Library. Use it when someone asks for an introduction, a greeting, or a name and age combined into a sentence.
---

# Build an introduction

Use the **Introduce Yourself** node if the user just wants the result. It takes `first_name`, `last_name`, and `age`, and returns `introduction`. Set the three inputs and run it.

If the user wants the steps visible or wants to change them, build the flow from three nodes:

1. Create a `CreateName` node and set `first_name` and `last_name`.
1. Create an `Age` node and set `age` between 1 and 98.
1. Create a `CreateIntroduction` node.
1. Connect `full_name` from `CreateName` to `full_name` on `CreateIntroduction`, and `age` from `Age` to `age`.
1. Run `CreateIntroduction`. The `introduction` output has the sentence.

To make it pig latin, connect `introduction` to the `input` of a `ConvertToPigLatin` node, and connect the two nodes' `exec_out` to `exec_in` so they run in order.

Read each node's page first for what its parameters do.
