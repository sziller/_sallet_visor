import inspect


def generate_asciidoc_from_class(cls):
    # Create a header for the class
    docstrings = [f"== Class: {cls.__name__}\n"]

    # Get all methods and attributes of the class
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        # Get the docstring
        docstring = inspect.getdoc(method)

        # Add method name as section
        docstrings.append(f"=== Method: `{name}`")

        # Add the docstring content, or a placeholder if no docstring is available
        if docstring:
            docstrings.append(f"\n{docstring}\n")
        else:
            docstrings.append("\n_No docstring available_\n")

    # Return the formatted AsciiDoc
    return "\n".join(docstrings)


# Example usage with a sample class
class MyClass:
    """This is MyClass"""

    def method_one(self):
        """This method does something."""
        pass

    def method_two(self, param):
        """This method takes a parameter."""
        pass

    def method_without_docstring(self):
        pass


if __name__ == "__main__":
    from SalletNodePackage.BitcoinNodeObject import *
    adoc = generate_asciidoc_from_class(Node)
    print(adoc)
