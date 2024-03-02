# pkl-python

Python bindings for Pkl.

## Installation (dev)

### Using `rye`
1. Install `rye`: https://rye-up.com/guide/installation/
1. Run `rye sync` from the root of this directory
1. Run `. .venv/bin/activate` to activate the virtualenv

### `pip` only
1. Create a virtualenv and activate it
1. `pip install -r requirements.lock`

## Example

`tests/test_evaluator.py` contains an example of how to setup and invoke the evaluator for a Pkl module. To run:

```
export PKL_EXEC=$(which pkl)
python tests/test_evaluator.py
```