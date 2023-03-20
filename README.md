# Notebook-doc

Notebook-doc is a Python package that can create documentation for functions in Databricks notebooks.

It can generate documentation from the docstrings of functions.

It will generate documentation as HTML documents, which can be displayed inside Databricks notebooks.

## Usage

The package can be used as follows to generate documentation:

1. Install the package (using PyPi - coming soon)
2. Import the documentation generator function as follows:
   ```{python}
   from notebook_doc import render_documentation
   ```
3. Make sure that you have executed all cells that contain function definitions.
4. Execute `render_documentation` function and provide the globals() dictionary to generate documentation as a HTML script.

### Example (in Databricks)

Databricks `displayHTML` function can be directly used to display the HTML document returned by the `render_documentation` function.

```{python}
from notebook_doc import render_documentation

displayHTML(render_documentation(globals(), module_name='Dummy Module'))
```

### Example (in other notebooks)

HTML output from `render_documentation` function can be written on a local HTML file so that documentation can be displayed as a HTML file.

```{python}
from notebook_doc import render_documentation

html_output = render_documentation(globals(), module_name='Dummy Module')

with open('dummy_doc.html', 'w') as f:
    f.write(html_output)
```
