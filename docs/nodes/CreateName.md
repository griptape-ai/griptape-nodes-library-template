---
description: Joins a first and last name into a full name, capitalizing both.
when_to_use: Use it when you have a first and last name as separate pieces and want one clean full name.
---

## When to use it

You collect a first name and a last name separately, maybe from two text boxes or two inputs, and a later node wants one `full_name`. This node fixes the capitalization and joins them.

## Example

[Introduce Yourself in Pig Latin](../workflows/introduce_yourself_in_pig_latin.md) uses it to feed the introduction node.

## Parameters

### first_name

Capitalized for you, so "maria" becomes "Maria". Only the first letter changes. The rest of the name stays as typed.

### last_name

Capitalized the same way as `first_name`.

### full_name

The two names joined by a space. This is the output to connect onward.
