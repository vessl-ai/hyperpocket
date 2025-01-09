# HyperPocket Docs

## How To Add New Document

Follow these steps to add a new document to HyperPocket Docs:

1. Add the new README file to the managed directory.
2. Update the `_templates/autoapi/index.rst` file by adding a reference to the new document. For example:

```text
Introduction
============

This is hyperpocket.

.. toctree::
   :hidden:

   Getting Started </autoapi/managed/getting_started.md>
   Conceptual Guide </autoapi/managed/conceptual_guide.md>
   Quick Start </autoapi/managed/quick_start.md>
   API Reference </autoapi/hyperpocket/index>
    
    <-- Add Hear -->
```

3. Submit a pull request for your changes.
4. Once reviewed, merge the pull request into the main branch.

## How To Edit Existing Document

To update an existing document:

1. Edit the relevant file in the managed directory.
2. Submit a pull request for your changes.
3. After review, merge the pull request into the main branch.