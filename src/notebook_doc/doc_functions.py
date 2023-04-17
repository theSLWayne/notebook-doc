from docstring_parser import parse
from jinja2 import Template
import os
import inspect
from typing import get_type_hints, Union, get_origin, get_args

def get_functions(globals_dict: dict) -> dict:
    """Get names and details of all functions executed in the given notebook

    Returns:
        Dictionary of function names and their details, indexed by function names.
    """

    docstrings = {}

    # List of functions
    func_list = [
        func_name
        for func_name in globals_dict
        if callable(globals_dict[func_name])
        and globals_dict[func_name].__module__ == "__main__"
    ]

    # List of docstrings
    docstring_list = [globals_dict[func_name].__doc__ for func_name in func_list]
    # Functions headers
    func_head_list = [
        f"{func_name}{inspect.signature(globals_dict[func_name])}"
        for func_name in func_list
    ]

    # List of parameter types
    func_type_list = []

    # List of return types
    ret_type_list = []

    # Types of all parameters and returns of the function
    for func in func_list:
        param_names = [
            param.name
            for param in inspect.signature(globals_dict[func]).parameters.values()
        ]
        type_hints = get_type_hints(globals_dict[func])
        if len(param_names) > 0:
            # If there are parameters, get their types from type hints if they are available
            names_types = {}
            for param_name in param_names:
                if param_name in type_hints:
                    if get_origin(type_hints[param_name]) is Union:
                        types = [
                            type_hint.__name__
                            for type_hint in list(get_args(type_hints[param_name]))
                        ]
                        names_types[param_name] = " or ".join(types)
                    else:
                        try:
                            names_types[param_name] = type_hints[param_name].__name__
                        except AttributeError:
                            names_types[param_name] = None
                else:
                    names_types[param_name] = None
            func_type_list.append(names_types)
        else:
            # If not, add None
            func_type_list.append(None)

        if "return" in type_hints:
            if get_origin(type_hints["return"]) is Union:
                types = [
                    type_hint.__name__
                    for type_hint in list(get_args(type_hints["return"]))
                ]
                ret_type_list.append(" or ".join(types))
            else:
                ret_type_list.append(type_hints["return"].__name__)
        else:
            ret_type_list.append(None)

    # Dictionary containing function details
    for func_name, docstring, func_head, func_types, ret_type in zip(
        func_list, docstring_list, func_head_list, func_type_list, ret_type_list
    ):
        docstrings[func_name] = [
            func_head,
            docstring if docstring is not None else "",
            func_types,
            ret_type,
        ]

    return docstrings


def parse_docstrings(docstrings: dict) -> list:
    """Extract information from docstrings using a docstring parser.

    Args:
        docstrings: A dictionary of docstrings

    Returns:
        A list of dicts that contain details about parsed docstrings.
    """

    # Functions list
    funcs = []

    # Iterating through the functions and their docstrings
    for func_name, strings in docstrings.items():
        func_head, docstring, types, ret_type = (
            strings[0],
            strings[1],
            strings[2],
            strings[3],
        )
        # Parse docstring
        parsed_docstring = parse(docstring)
        # Create detailed profile for the function
        func_details = {
            "name": func_name,
            "head": func_head,
            "short_description": parsed_docstring.short_description,
            "long_description": parsed_docstring.long_description.replace(
                "\n", "<br>"
            ).replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
            if parsed_docstring.long_description
            else parsed_docstring.long_description,
            "args": [
                {
                    "arg_name": arg.arg_name,
                    "arg_type": types[arg.arg_name]
                    if arg.arg_name in types
                    else arg.type_name,
                    "is_optional": arg.is_optional,
                    "default": arg.default,
                    "description": arg.description,
                }
                for arg in parsed_docstring.params
            ]
            if parsed_docstring.params is not None
            else None,
            "raises": [
                {
                    "type": raises.type_name,
                    "description": raises.description.replace("\n", "<br>").replace(
                        "\t", "&nbsp;&nbsp;&nbsp;&nbsp;"
                    ),
                }
                for raises in parsed_docstring.raises
            ]
            if parsed_docstring.raises is not None
            else None,
            "returns": {
                "name": parsed_docstring.returns.return_name,
                "type": ret_type
                if ret_type is not None
                else parsed_docstring.returns.type_name,
                "description": parsed_docstring.returns.description.replace(
                    "\n", "<br>"
                ).replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;"),
            }
            if parsed_docstring.returns is not None
            else None,
            "examples": [
                {
                    "description": example.description.replace("\n", "<br>").replace(
                        "\t", "&nbsp;&nbsp;&nbsp;&nbsp;"
                    ),
                    "snippet": example.snippet,
                }
                for example in parsed_docstring.examples
            ]
            if parsed_docstring.examples is not None
            else None,
        }
        funcs.append(func_details)

    return funcs


def generate_html(docstrings: list, title: str, enable_links:bool) -> str:
    """Generate HTML file documenting the functions

    Generate HTML code that displays the functions and their docstrings as documentation.

    Args:
        docstrings: The list that includes details about each function
        title: Title of the module or the notebook
        enable_links: Whether to enable links in the generated HTML document

    Returns:
        Rendered HTML document as a string.
    """

    # Create HTML template to display the documentation as a HTML file
    template = Template(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>{{ title }} - Documentation</title>

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD" crossorigin="anonymous">
    </head>
    <body class="bg-secondary">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js" integrity="sha384-w76AqPfDkMBDXo30jS1Sgez6pr3x5MlQ1ZAGC+nuZB+EYdgRZgiwxhTBTkF7CXvN" crossorigin="anonymous"></script>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container" id="top">
                <span class="navbar-text">
                    <h3 class="display-5"> {{ title }} - Documentation </h3>
                </span>
            </div>
        </nav>
        <div class="container bg-light">
        <div class="row">
            <div class="col-3">
                {% if links %}
                    <div class="container sticky-top">
                        <br>
                        <h5>Functions List</h5>
                        <div class="card">
                            <ul class="list-group list-group-flush">
                            {% for docstring in docstrings %}
                                <a href="#{{ docstring.name }}" style="text-decoration: none; color: black;"><li class="list-group-item">{{ docstring.name }}</li></a>
                            {% endfor %}
                            </ul>
                        </div>
                    </div>
                {% else %}
                    <div class="container sticky-top">
                        <br>
                        <h5>Functions List</h5>
                        <div class="card">
                            <ul class="list-group list-group-flush">
                            {% for docstring in docstrings %}
                                <li class="list-group-item">{{ docstring.name }}</li>
                            {% endfor %}
                            </ul>
                        </div>
                    </div>
                {% endif %}
            </div>
            <div class="col">
            <h5 class="display-6">Functions</h4>
            {% for docstring in docstrings %}
                <div id="{{ docstring.name }}">
                <p class="h3"> {{ docstring.name }} </p>
                <div class="card">
                    <div class="card-header"><i><b>{{ docstring.head }}</b></i></div>
                    <div class="container">
                        {% if docstring.short_description is not none %}
                            <p class="card-title"> {{ docstring.short_description }} </p>
                        {% endif %}
                        {% if docstring.long_description is not none %}
                            <p class="card-text"> {{ docstring.long_description }} </p>
                        {% endif %}
                        <b>Args:</b>
                        {% if docstring.args|length > 0 %}
                            <ul class="list-group list-group-flush">
                            {% for arg in docstring.args %}
                                <li class="list-group-item"> <i>{{ arg.arg_name }}</i>: {{ arg.description }} {% if arg.arg_type is not none %}({{ arg.arg_type }}){% endif %} </li>
                            {% endfor %}
                            </ul>
                        {% else %}
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item"><i>None</i></li>
                            </ul>
                        {% endif %}
                        <b>Returns:</b>
                        {% if docstring.returns is not none %}
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item"> {% if docstring.returns.type is not none %}({{ docstring.returns.type }}){% endif %} {{ docstring.returns.description }} </li>
                            </ul>
                        {% else %}
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item"> None </li>
                            </ul>
                        {% endif %}
                        {% if docstring.raises|length > 0 %}
                            <b>Raises:</b>
                            <ul class="list-group list-group-flush">
                            {% for raise in docstring.raises %}
                                <li class="list-group-item"> <i>{{ raise.type }}</i>: {{ raise.description }} </li>
                            {% endfor %}
                            </ul>
                        {% endif %}
                        {% if docstring.examples|length > 0 %}
                            <b>Examples:</b>
                            <ul class="list-group list-group-flush">
                                {% for example in docstring.examples %}
                                <li class="list-group-item">
                                    <div class="card">
                                        <div class="card-header">
                                            {{ example.description | safe }}
                                        </div>
                                    </div>
                                </li>
                            {% endfor %}
                            </ul>
                        {% endif %}
                    </div>
                </div>
                </div>
                <br>               
            {% endfor %}
            <br>
            </div>
        </div>
        </div>
        <br>
        <br>
        <nav class="navbar navbar-light bg-dark">
        </nav>

    </body>

    </html>
    """
    )

    # Render the HTML template with function details
    html = template.render({"docstrings": docstrings, "title": title, "links": enable_links})

    return html


def render_documentation(globals_dict: dict, module_name: str = None, enable_links: bool = False) -> str:
    """Render documentation for a given notebook.

    Entry point to all functions - this should be invoked inside of the notebook to generate documentation for a notebook.

    Args:
        globals_dict: globels() object
        module_name: Name of the module that is being documented. Optional. Will use 'Notebook' if not provided.
        enable_links: Whether to enable links in the generated HTML document. This will include links for each function
                    documentation on the left side of the HTML page. Recommended only if you are writing HTML documentation
                    into a HTML file. These links will not work with Databricks generateHTML method. Optional. Defaulted to False.

    Returns:
        Documentation as HTML script

    Examples:
        Run the function as following with the name of the module:

        >>> render_documentation(module_name="Dummy Module")
        ... HTML script

        Or the function can be invoked without the module name. ('Notebook' will be used as the module name in this case):

        >>> render_documentation()
        ... HTML script
    """

    docstrings = get_functions(globals_dict)
    parsed_docstrings = parse_docstrings(docstrings)
    html_docs = generate_html(
        docstrings=parsed_docstrings,
        title=module_name if module_name is not None else "Notebook",
        enable_links=enable_links
    )

    return html_docs
