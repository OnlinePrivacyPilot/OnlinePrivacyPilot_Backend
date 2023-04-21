import json
from src import opp
from src import storage
import sys
import getopt

class cliClient:
    def __init__(self):
        self.run()

    def cli_usage(self,output):
        program_name = sys.argv[0].split("/")[-1]
        print(f"Usage: {program_name} [OPTIONS] <target>\n", file=output)
        print("General:", file=output)
        print("\t-h,\t--help\t\t\tprint this help.", file=output)
        print("\t-d,\t--depth\t\t\tspecify the maximum depth of the search.", file=output)
        print("\t-n,\t--negative-filter\tspecify one optional negative filter.", file=output)
        print("\t-p,\t--positive-filter\tspecify one optional positive filter.", file=output)
        print("\t-o,\t--active_search\t\tTrue or False: if activated, OPP will trigger osint techniques", file=output)
        print("\t-k,\t--api_key\t\tto be furnished by the user, if not will scrap", file=output)
        print("\n", file=output)

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hdnpok", ["help", "depth=", "negative-filter=", "positive-filter=", "active_search=", "api_key="])
        except getopt.GetoptError as error:
            print(str(error), file=sys.stderr)
            sys.exit(2)

        if len(args) == 0:
            self.cli_usage(sys.stderr)
            sys.exit(2)

        # Default search depth
        search_depth = 3
        initial_filters = []
        active_search = True
        api_key = ""

        for opt, value in opts:
            if opt in ["-h", "--help"]:
                self.cli_usage(sys.stdout)
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
                active_search = value.lower() in ("yes", "true", "t", "1")
            elif opt in ["-k", "--api_key"]:
                api_key = value

        config = {
            "api_key": api_key,
            "active_search": active_search
            }

        json_str = json.dumps(config)

        with open("config.json", "w") as f:
            f.write(json_str)

        fingerprint = opp.OPP(target=" ".join(args), search_depth=search_depth, initial_filters = initial_filters)
        storage.Storage().store_graph(fingerprint.get_fingerprint())
        storage.Storage().gen_graphviz()
        storage.Storage().tree_build(fingerprint.get_fingerprint())
