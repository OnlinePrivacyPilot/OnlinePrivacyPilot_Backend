from opp import fingerprint_handler
from opp import storage
from opp import search
import sys
import getopt
from asciitree import LeftAligned

def cli_usage(output: str):
    """ This function prints help for OPP CLI client in the given output.

    Args:
        output (str): Output to print in.
    """
    program_name = sys.argv[0].split("/")[-1]
    print(f"Usage: {program_name} [OPTIONS] <target>\n", file=output)
    print("General:", file=output)
    print("\t-h,\t--help\t\t\tprint this help.", file=output)
    print("\t-d,\t--depth\t\t\tspecify the maximum depth of the search.", file=output)
    print("\t-n,\t--negative-filter\tspecify optional negative filter.", file=output)
    print("\t-p,\t--positive-filter\tspecify optional positive filter.", file=output)
    print("\t-o,\t--active_search\t\tactivate OSINT techniques in the research process", file=output)
    print("\t-q,\t--quiet\t\t\tdisable the display of the ascii tree in output", file=output)
    print("\t-s,\t--store\t\t\tstore obtained fingerprint as : none (default), db (SQLITE file only), dot (SQLITE file + DOT file + PNG)", file=output)
    print("\t-k,\t--api_key\t\tspecify Google search API Key, if empty, the program will get results using a scrapping library", file=output)
    print("\t-c,\t--cse_id\t\tspecify Custom Search Engine ID, if empty, the program will get results using a scrapping library", file=output)
    print("\n", file=output)

def run():
    """
    This function handles the command line interface of OPP

    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:n:p:ok:c:qs:", ["help", "depth=", "negative-filter=", "positive-filter=", "active_search=", "api_key=", "cse_id=", "quiet", "store="])
    except getopt.GetoptError as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)

    if len(args) == 0:
        cli_usage(sys.stderr)
        sys.exit(2)

    # Default search depth
    search_depth = 3
    initial_filters = []
    active_search = False
    api_key = ""
    cse_id = ""
    quiet = False
    store = "none"

    for opt, value in opts:
        if opt in ["-h", "--help"]:
            cli_usage(sys.stdout)
            sys.exit(0)
        elif opt in ["-d", "--depth"]:
            search_depth = int(value)
        elif opt in ["-n", "--negative-filter"]:
            initial_filters.append(
            {
                "value" : value,
                "type" : None,
                "positive" : False
            })
        elif opt in ["-p", "--positive-filter"]:
            initial_filters.append(
            {
                "value" : value,
                "type" : None,
                "positive" : True
            })
        elif opt in ["-o", "--active_search"]:
            active_search = True
        elif opt in ["-k", "--api_key"]:
            api_key = value
        elif opt in ["-c", "--cse_id"]:
            cse_id = value
        elif opt in ["-q", "--quiet"]:
            quiet = True
        elif opt in ["-s", "--store"]:
            if value in ["db", "dot"]:
                store = value

    # Set search options
    search.SearchOptions()
    search.SearchOptions().set_api_key(api_key=api_key)
    search.SearchOptions().set_cse_id(cse_id=cse_id)
    search.SearchOptions().set_active_search(active_search=active_search)
    # Generate Fingerprint
    research_instance = fingerprint_handler.FingerprintHandler(target=" ".join(args), search_depth=search_depth, initial_filters = initial_filters)
    fingerprint = research_instance.get_fingerprint()

    # Console output
    if not quiet:
        print(LeftAligned()(research_instance.get_ascii_tree(fingerprint)))
    
    # Results storage
    if store in ["db", "dot"]:
        db = storage.Storage("_".join(args).replace(' ', '_')+".db")
        db.store_graph(fingerprint)
    if store == "dot":
        db.gen_graphviz()

if __name__ == '__main__':
    run()
