# Manticore Provisioner
A Python wrapper around Ansible to automatically provision Manticore jobs both locally and in the cloud

## Running a job via `mcorepv`

`mcorepv` is a python-based wrapper around Manticore CLI and Ansible that can provision jobs locally and in the cloud. It takes all known Manticore CLI flags along with a few others down below.

### Installation 

* Run `python3 setup.py develop` to install mcorepv and all its dependencies.

### Local provisioning

Specify the `--local` flag for `mcorepv` to run a job locally.

* `mcorepv --local -- <executable_to_analyze> --<manticore_flags>`
* `mcorepv --local -- <some_script.py>`

The first command runs Manticore analysis on a binary, whereas the second runs a python script.

### Remote provisioning

Configuration data will be stored in the `.mcorepv_config` file. This file is stored in `~` and a per-project copy is generated in each directory in which `mcorepv` is run.

Specify the `--remote` flag for `mcorepv` to provision a DigitalOcean instance and run a Manticore job on the instance. The following denotes a few general usages of `mcorepv` for remote jobs.

* `mcorepv --remote -- <some_script.py> target.sol`
* `mcorepv --remote -- <binary_to_analyze> --verbosity 3`
* `mcorepv --remote -- contract.sol --txaccount attacker`

## Running a job directly via `ansible-playbook`

### Initial Setup

Assuming the python dependencies are already installed:
* Navigate to `vars/`
* In droplet.yml, set the value of `droplet_ssh_key` to the path of the public key file (e.g. for an ed25519 key in `/.ssh/id_ed25519.pub`, set `droplet_ssh_key` to `"{{ lookup('file', lookup('env','HOME') + '/.ssh/id_ed25519.pub') }}")`
* In ansible.yml, change the value of the variables (droplet name, username, etc) to be as desired.
* Run `ansible-playbook -vvv digitalocean.yml`

### Tearing down the droplet
* Run `ansible-playbook -vvv tear_down_instance.yml`
* When provisioning and tearing down multiple instances, change the value of `droplet_name` in `vars/droplet.yml` to be the respective name of the instance to destroy.

## Variables

Below is a description of all variables necessary for configuration.

### vars/droplet.yml

`droplet.yml` holds droplet-oriented variables for the initial DigitalOcean droplet provisioning process.

* digital_ocean_api_token: DigitalOcean API key (DigitalOcean recommends pre-setting an environment variable `DO_TOKEN` and including its contents via  `"{{ lookup('env','DO_TOKEN') }}"`)
* ssh_key_name: name of SSH key to put on server. *_Must be unique!!_*
* droplet_region: region in which to provision an instance
* droplet_size: desired size of droplet
* droplet_image: OS / distribution of droplet
* droplet_name: desired name of droplet
* droplet_ssh_key: path to SSH public key to copy to server (defined as `"{{ lookup('file', lookup('env','HOME') + '/.ssh/<key_name>') }}"`)

### vars/ansible.yml

`ansible.yml` holds user-oriented variables for the provisioned DigitalOcean droplet instance.

* manticore_env: directory in which Manticore scripts will be run
* manticore_script: script inside of manticore_env to run
* remote_uname: username on the droplet
* working_dir: current working directory on local machine
* logfile: log file of Manticore script that will be saved under working_dir
* main_cmd: command to run on remote droplet (i.e. `manticore` or `python3`)
* flags: flags to pass into Manticore on remote droplet

## Known issues
* Sometimes if the SSH service on the droplet times out, a permission denied error will occur when re-running the `digitalocean.yml` script.  To solve this issue, run `ansible-playbook reset_ssh_key.yml -vv` to reset the SSH key on the server.  As an additional restriction, the `ssh_key_name` field in `vars/droplet.yml` must be unique per user.
* Real-time logging really only works well if the script being run takes a long time to complete and outputs a large amount of data to stdout. It's also clunky and should be largely superseded by the TUI. We should strip it out if we can't substantially improve it.
* OSX Python occasionally has SSL errors when working with Ansible. See: https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify


# Manticore TUI
This repository also contains the code for the Manticore TUI. Eventually, the provisioner will automatically spawn the TUI when Manticore is invoked.

## TUI demo
With two terminal windows open:
* Run `python3 server.py` in one window
* Run `python3 tui.py` in another
* Observe

![TUI Image](https://raw.githubusercontent.com/trailofbits/mc-ansible/master/tui.png)