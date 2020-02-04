import yaml
import glob
from pathlib import Path
from prompt_toolkit import prompt
from getpass import getuser
from shutil import copyfile

repo_url = "https://github.com/trailofbits/mc-ansible.git"
ansible_yml_path = ".mcore_config/vars/ansible.yml"
droplet_yml_path = ".mcore_config/vars/droplet.yml"


def create_config_file(target, existing_vars):
    skip = {
        "manticore_env",
        "working_dir",
        "droplet_image",
        "logfile",
        "manticore_script",
        "main_cmd",
        "version",
    }

    prompts = {
        "remote_uname": "Enter the username to use on the remote server",
        "digital_ocean_api_token": "Enter your Digital Ocean API Token",
        "droplet_region": "Enter the region to create your instance in",
        "droplet_size": "Enter your desired droplet size",
        "droplet_name": f"Enter your desired droplet hostname",
        "droplet_ssh_key": "Pick an SSH public key to use with DigitalOcean",
        "ssh_key_name": "Enter the name of this SSH key on DigitalOcean",
    }

    vars_internal = {}

    print("Configure ansible variables:")

    for var in existing_vars.keys():
        if var == "droplet_ssh_key":
            sshdir = Path.home().joinpath(".ssh")
            keys = list(glob.glob(str(sshdir.joinpath("*.pub"))))
            assert keys, "No SSH public keys found in ~/.ssh"
            vars_internal[var] = prompt(f"{prompts.get(var, var)}: ", default=keys[0])
        elif var in skip:
            pass
        else:
            vars_internal[var] = prompt(
                f"{prompts.get(var, var)}: ", default=existing_vars[var]
            )

    with open(target, "w") as outf:
        yaml.dump(vars_internal, outf, default_flow_style=False)

    print("Config file saved to", target)
    return vars_internal


def load_config_file(target):
    with open(target, "r") as yamlf:
        return yaml.safe_load(yamlf)


def initial_setup():

    global_config = Path.home().joinpath(".mcorepv_config")
    local_config = Path.cwd().joinpath(".mcorepv_config")
    existing = {
        "manticore_env": "manticore_job",
        "manticore_script": "",
        "remote_uname": getuser(),
        "working_dir": "{{ lookup('env','PWD') }}",
        "logfile": "{{ working_dir }}/manticore_logs",
        "main_cmd": "manticore",
        "digital_ocean_api_token": "{{ lookup('env', 'DO_TOKEN') }} # Grab token from DO_TOKEN environment variable",
        "droplet_region": "nyc1",
        "droplet_size": "512mb",
        "droplet_image": "ubuntu-18-04-x64",
        "droplet_name": f"{getuser()}-mc-ansible",
        "droplet_ssh_key": "",
        "ssh_key_name": "",
        "version": 0,
    }

    if not global_config.exists():
        print("No global config file found! Creating...")
        existing.update(create_config_file(global_config, existing))

    existing.update(load_config_file(global_config))

    print("Creating local config...")
    if input("Use global configuration? (y/n) ").lower().strip() in {"n", "no"}:
        create_config_file(local_config, existing)
    else:
        copyfile(str(global_config), str(local_config))


if __name__ == "__main__":
    initial_setup()
