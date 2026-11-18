---
description: Takes a first name, a last name, and an age, and returns a short introduction.
when_to_use: Use it when you want the whole name-to-introduction flow as a single node.
---

## When to use it

You want the result of [Getting started](../guides/getting-started.md) without placing the three nodes yourself. This is a saved workflow that behaves like one node. It runs [Create a Name](../nodes/CreateName.md) and [Create an Introduction](../nodes/control/create_an_introduction.md) inside.

## Example

Drag it in, type a first name, a last name, and an age, and run it. The `introduction` output has your sentence.

## Parameters

### first_name

The first name. Capitalized for you.

### last_name

The last name. Capitalized for you.

### age

A whole number.

### introduction

The finished sentence.
