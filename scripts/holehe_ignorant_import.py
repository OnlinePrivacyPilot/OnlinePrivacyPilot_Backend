import importlib
import pkgutil
import holehe
import ignorant

def import_submodules(package: str, recursive=True) -> list:
    """ This function imports all submodules from given package and returns the list these submodules. 

    Args:
        package (str): Package to import from.
        recursive (bool, optional): Defines if necessary to import recursively. Defaults to True.

    Returns:
        list: Imported submodules.
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def print_imports(modules) -> list:
    imports = ""
    for module in modules:
        if len(module.split(".")) > 3 :
            imports += "from " + module + " import " + module.split(".")[-1] + " as " + module.split(".")[0] + "_" + module.split(".")[-1] + "\n"
    return imports

def print_websites(modules) -> list:
    return "WEBSITES_" + list(modules.keys())[0].split(".")[0] + " = " + str([m.split(".")[0] + "_" + m.split(".")[-1] for m in modules if len(m.split(".")) > 3]).replace("'","") + "\n"

file = open("opp/osint_imports.py", "w")
holehe_modules = import_submodules(holehe)
ignorant_modules = import_submodules(ignorant)
file.write(print_imports(holehe_modules))
file.write(print_imports(ignorant_modules))
if holehe_modules:
    file.write(print_websites(holehe_modules))
if ignorant_modules:
    file.write(print_websites(ignorant_modules))
file.close()
