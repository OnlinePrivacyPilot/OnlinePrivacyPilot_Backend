from src import opp
import sys
import getopt

class cliClient:
    def __init__(self):
        self.run()

    def cli_usage(self, output):
        program_name = sys.argv[0].split("/")[-1]
        print(f"Usage: {program_name} [OPTIONS] <target>\n", file=output)
        print("General:", file=output)
        print("\t-h,\t--help\t\t\tprint this help.", file=output)
        print("\t-d,\t--depth\t\t\tspecify the maximun depth of the search.", file=output)
        print("\n", file=output)

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "depth="])
        except getopt.GetoptError as error:
            print(str(error), file=sys.stderr)
            sys.exit(2)

        if len(args) == 0:
            self.cli_usage(sys.stderr)
            sys.exit(2)

        # Default search depth
        search_depth = 3

        for opt, value in opts:
            if opt in ["-h", "--help"]:
                self.cli_usage(sys.stdout)
                sys.exit(0)
            elif opt in ["-d", "--depth"]:
                search_depth = int(value)

        fingerprint = opp.OPP(target = " ".join(args), search_depth = search_depth)
