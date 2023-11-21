import re
import subprocess
import json
import time
import datetime
import sys
import argparse
import dateutil.parser as dateparser

import yaml
import tqdm


def read_env(filepath: str) -> dict:
    """Reading and parsing a yaml file."""
    print(f"Reading environment in {filepath}")
    with open(filepath, "r") as f:
        content = "".join(f.readlines())
    env = yaml.load(content, Loader=yaml.Loader)
    return env


def channel_str(env: dict) -> str:
    """Extract the channel argument for conda from a parsed environment file."""
    if "channels" in env:
        return "-c " + " -c ".join(env["channels"])
    else:
        return ""


def parse_dependency(dep: str) -> (str, str):
    """Parse dependency string into package name and version constraint."""
    comps = re.split("<|>|=| ", dep)
    package = comps[0]
    constraint = dep[len(package) :].strip()

    return package, constraint


def pin_dependency(dep: str, channels: str, date: int) -> str:
    """Construct a constraint on `dep` based on `date` (unix time)."""
    package, constraint = parse_dependency(dep)
    res = subprocess.run(
        ["conda", "repoquery", "search", package, "--json"] + channels.split(),
        capture_output=True,
    )
    res.check_returncode()
    pkg_info = json.loads(res.stdout)
    query_res = pkg_info["result"]["status"]
    if query_res != "OK":
        raise ValueError(f"Bad query result ({query_res}) for {package}")
    packages = pkg_info["result"]["pkgs"]
    valid_versions = [p["version"] for p in packages if p["timestamp"] <= date]
    constraint = " <=" + valid_versions[0] + ((", " + constraint) if len(constraint) > 0 else "")

    return package + constraint


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="process.py",
        description="""
Try to approximately rewind time for a conda environment.
A new conda file is generated with a version constraint
correspondin to the date.""",
    )
    parser.add_argument("environment-file", help="conda environment file")
    parser.add_argument("date", help="target date, e.g. 2022-11-20")
    parser.add_argument("-o", "--output", help="output environment file", default="/dev/stdout")
    return parser


if __name__ == "__main__":
    parser = argument_parser()
    args = vars(parser.parse_args())

    env = read_env(args["environment-file"])
    date = time.mktime(dateparser.parse(args["date"]).timetuple())
    print(f"Rewinding to {date}")
    channels = channel_str(env)
    env["dependencies"] = [
        (pin_dependency(dep, channels, date) if isinstance(dep, str) else dep)
        for dep in tqdm.tqdm(env["dependencies"])
    ]
    with open(args["output"], "w") as f:
        f.write(yaml.dump(env))
