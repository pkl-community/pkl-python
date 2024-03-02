from urllib.parse import urlparse
import os


# ModuleSource represents a source for Pkl evaluation.
class ModuleSource:
    # uri is the URL of the resource.
    # Contents is the text contents of the resource, if any.
    #
    # If Contents is not provided, it gets resolved by Pkl during evaluation time.
    # If the scheme of the Uri matches a ModuleReader, it will be used to resolve the module.
    def __init__(self, uri, contents=None):
        self.uri = uri
        self.contents = contents


# FileSource builds a ModuleSource, treating its arguments as paths on the file system.
#
# If the provided path is not an absolute path, it will be resolved against the current working
# directory.
#
# If multiple path arguments are provided, they are joined as multiple elements of the path.
def FileSource(*pathElems):
    src = os.path.join(*pathElems)
    src = os.path.abspath(src)
    return ModuleSource(f"file://{src}")


replTextUri = "repl:text"


# TextSource builds a ModuleSource whose contents are the provided text.
def TextSource(text):
    return ModuleSource(replTextUri, text)


# UriSource builds a ModuleSource using the input uri.
def UriSource(uri):
    parsedUri = urlparse(uri)
    return ModuleSource(parsedUri.geturl())
