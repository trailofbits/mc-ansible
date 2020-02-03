import os
import yaml
import git
import logging

repo_url = "https://github.com/pwang00/Ansible-Manticore.git"
ansible_yml_path = ".mcore_config/vars/ansible.yml"
droplet_yml_path = ".mcore_config/vars/droplet.yml"

ansible_vars = {
    "manticore_env": None,
    "manticore_script": None,
    "remote_uname": None,
    "working_dir": "{{ lookup('env','PWD') }}",
    "logfile": None,
    "main_cmd": None,
}

digitalocean_vars = {
    "digital_ocean_api_token": "{{ lookup('env', 'DO_TOKEN') }}",
    "ssh_key_name": None,
    "droplet_region": None,
    "droplet_size": None,
    "droplet_name": None,
    "droplet_ssh_key": "{{ lookup('file', lookup('env','HOME') + '/.ssh/id_ed25519.pub') }}",
}


def initial_setup():

    print(f".mcore_config directory not found, cloning from {repo_url}")

    git.Repo.clone_from(repo_url, ".mcore_config", branch="master")

    if input("Use default configuration? (y/n) ").lower() == "n":

        print("Configure ansible variables: \n")

        for var in ansible_vars.keys():
            ansible_vars[var] = input(f"{var}: ")

        print("Configure remote droplet variables: \n")

        for var in digitalocean_vars.keys():

            if var == "droplet_ssh_key":
                digitalocean_vars[var] = (
                    "{{ lookup('file', lookup('env','HOME')" + input(f"{var}: ") + ")}}"
                )
            else:
                digitalocean_vars[var] = input(f"{var}: ")

        with open(ansible_yml_path) as ansible_config, open(
            droplet_yml_path
        ) as droplet_config:
            yaml.dump(ansible_vars, ansible_config, default_flow_style=False)
            yaml.dump(digitalocean_vars, droplet_config, default_flow_style=False)


if __name__ == "__main__":
    initial_setup()
