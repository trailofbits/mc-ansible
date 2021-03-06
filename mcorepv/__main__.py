#!/usr/bin/python3
""" Python wrapper built around supporting Manticore functionality"""

import argparse
import yaml
import subprocess
import time
import logging
from pathlib import Path

from .mcorepv_config import initial_setup, load_config_file

logging.basicConfig(
    filename="mcprov.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger("mcprov.main")
logger.setLevel(logging.DEBUG)

curdir = Path(__file__).parent.parent


def parse_arguments():
    parser = argparse.ArgumentParser(description="Wrapper around Manticore CLI")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-l", "--local", action="store_true", help="Run Manticore on the local machine"
    )
    group.add_argument(
        "-r",
        "--remote",
        action="store_true",
        help="Run Manticore on the remote machine",
    )
    group.add_argument(
        "--playbook",
        type=str,
        default="digitalocean.yml",
        help="Manually run one of the Ansible playbooks",
    )
    group.add_argument(
        "--teardown",
        action="store_true",
        help="Destroy a previously provisioned droplet",
    )
    group.add_argument(
        "--config", action="store_true", help="Rebuild the local config file"
    )

    parser.add_argument(
        "-v",
        action="count",
        default=1,
        help="Specify Ansible verbosity level from -v to -vvvv",
    )

    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to be passed to Manticore"
    )
    parsed = parser.parse_args()

    return parsed


def main(parsed=parse_arguments()):
    involves_ansible = parsed.remote or parsed.teardown or parsed.playbook

    if involves_ansible and not Path.cwd().joinpath(".mcorepv_config").exists():
        logger.warning("Creating config file...")
        initial_setup()

    if parsed.config:
        initial_setup()
        exit(0)

    if involves_ansible:
        user_config = load_config_file(Path.cwd().joinpath(".mcorepv_config"))
        droplet_config = load_config_file(curdir.joinpath("vars", "droplet.yml"))
        ansible_config = load_config_file(curdir.joinpath("vars", "ansible.yml"))

        for var in droplet_config:
            droplet_config[var] = user_config.get(var, droplet_config[var])
        for var in ansible_config:
            ansible_config[var] = user_config.get(var, ansible_config[var])

        with open(curdir.joinpath("vars", "droplet.yml"), "w") as dropf:
            yaml.dump(droplet_config, dropf, default_flow_style=False)
        with open(curdir.joinpath("vars", "ansible.yml"), "w") as ansiblef:
            yaml.dump(ansible_config, ansiblef, default_flow_style=False)

    if parsed.teardown:
        to_run = [
            "ansible-playbook",
            "--inventory",
            str(curdir.joinpath("hosts")),
            str(curdir.joinpath("tear_down_instance.yml")),
        ]

    elif parsed.playbook:
        to_run = [
            "ansible-playbook",
            "--inventory",
            str(curdir.joinpath("hosts")),
            str(curdir.joinpath(parsed.playbook)),
        ]

    if parsed.local or parsed.remote:
        assert (
            parsed.args
        ), "--remote and --local options require arguments to be specified after `--`"
        if parsed.args[0] == "--":
            parsed.args = parsed.args[1:]
        file = parsed.args[0]

    if parsed.local:
        to_run = ["python3"] if file.endswith(".py") else ["manticore"]
        to_run.extend(parsed.args)

    elif parsed.remote:
        to_run = [
            "ansible-playbook",
            "--inventory",
            str(curdir.joinpath("hosts")),
            str(curdir.joinpath(parsed.playbook)),
        ]

        if parsed.args:
            is_py_file = file.endswith(".py")

            command = "python3" if is_py_file else "manticore"

            to_run.append("--extra-vars")

            to_run.append(
                "manticore_script={} working_dir={}/ main_cmd={}".format(
                    " ".join(parsed.args), str(Path.cwd()), command
                )
            )

        to_run.append("-{}".format(parsed.v * "v"))

    process = subprocess.Popen(to_run)

    # Allows the user to prematurely kill the subprocess with KeyboardInterrupt

    try:
        while process is not None and process.poll() is None:
            time.sleep(0.1)
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    main()
