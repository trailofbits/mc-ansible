# Manticore Provisioner
A Python wrapper around Ansible to automatically provision Manticore jobs both locally and in the cloud

## Variables

Below is a description of all variables necessary for configuration.

### vars/droplet.yml

`droplet.yml` holds droplet-oriented variables for the initial DigitalOcean droplet provisioning process.

* digital_ocean_api_token: DigitalOcean API key (DigitalOcean recommends pre-setting an environment variable `DO_TOKEN` and including its contents via  `"{{ lookup('env','DO_TOKEN') }}"`)
* ssh_key_name: name of SSH key to put on server
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

## Running a job directly via `ansible-playbook`

### Initial Setup

(Warning: very rough and experimental)

* Run `pip3 install ansible "dopy>=0.3.7"` (currently uses digital_ocean which is meant to only be compatible with python2, but with a bit of tweaking can be made compatible with python3.  See Notes / Recommendations for more details.)
* Generate an SSH key via `ssh-keygen -t <key_type_here>`(stored in ~/.ssh/)
* Define an environment variable `DO_TOKEN` that holds the DigitalOcean API token in plaintext; (e.g. on Ubuntu run `export DO_TOKEN=<your_api_key_in_hexadecimal>`)
* Navigate to `vars/`
* In droplet.yml, set the value of `droplet_ssh_key` to the path of the public key file (e.g. for an ed25519 key in `/.ssh/id_ed25519.pub`, set `droplet_ssh_key` to `"{{ lookup('file', lookup('env','HOME') + '/.ssh/id_ed25519.pub') }}")`
* In ansible.yml, change the value of the variables (droplet name, username, etc) to be as desired.
* Run `ansible-playbook -vvv digitalocean.yml`

### Tearing down the droplet
* Run `ansible-playbook -vvv tear_down_instance.yml`
* When provisioning and tearing down multiple instances, change the value of `droplet_name` in `vars/droplet.yml` to be the respective name of the instance to destroy.

## Running a job via `mcorepv` (name subject to change)

`mcorepv` is a python-based wrapper around Manticore CLI and Ansible that can provision jobs locally and in the cloud. It takes all known Manticore CLI flags along with a few others down below.

### Installation 

* Run `python3 setup.py install --user` to install mcorepv and all its dependencies.

### Local provisioning

Specify the `--local` flag for `mcorepv` to run a job locally.  The following denote two general usages of `mcorepv --local`

* `mcorepv --local <executable_to_analyze> --<manticore_flags>`
* `mcorepv --local <manticore_python_script>`

The first command runs Manticore analysis on a binary, whereas the second runs a python script.

### Remote provisioning

Note: `mcorepv` config data should be stored in `.mcore_config` directory.  By default, `mcorepv` will check to see if a `.mcore_config` directory exists.  If not it will clone this git repository, allowing the user to either use default configurations or update all aforementioned [variables](https://github.com/pwang00/Ansible-Manticore/README.md#Variables).  `mcorepv` also allows the usage of custom playbooks, which are specified with the `--playbook` flag, as well as configuring Ansible logging verbosity, which is specified via the `--verbosity` flag.

Specify the `--remote` flag for `mcorepv` to provision a DigitalOcean instance and run a Manticore job on the instance. The following denotes a few general usages of `mcorepv` for remote jobs.

* `mcorepv --remote <manticore_python_script>`
* `mcorepv --remote <manticore_python_script> --playbook <custom_ansible_playbook>`
* `mcorepv --remote <binary_to_analyze> --verbosity 3`
* `mcorepv --remote <contract_to_analyze> contract.sol --txaccount attacker`
* `mcorepv --remote --destroy`

The first command executes the default Ansible playbook in `.mcore_config`, which provisions a DigitalOcean droplet runs a Manticore python script in the cloud.  The second command executes the tasks in a custom playbook.  The third and fourth commands demonstrate verbosity configuration and the passing of known flags to Manticore on the remote droplet.  The last command tears down a previously provisioned droplet by running the `tear_down_instance.yml` playbook .in `.mcore_config`.


### Notes / recommendations
* The current Ansible playbooks use the digital_ocean module, which was originally developed in python 2.  As such, when installing dopy via `pip3`, a `basestr` is not defined error will occur.  To fix this, open `~/.local/lib/python3.7/site-packages/dopy/manager.py` and change all occurrences of `basestr` to `str`. 
* As of Ansible 2.8, another module `digital_ocean_droplet` has been added, which does not require a prior `pip3 install`.  However, it has only one page of documentation (i.e. relatively poor support) and from what I've seen, is bug-ridden and error-prone. 

### Areas of improvement

* README currently is cluttered, should be made less verbose but get the point across.
* `mcorepv` may still be relatively buggy and unoptimized, and requires further testing.

### Known issues
* Sometimes if the SSH service on the droplet times out, a permission denied error will occur when re-running the `digitalocean.yml` script.  To solve this issue, run `ansible-playbook reset_ssh_key.yml -vv` to reset the SSH key on the server.  As an additional restriction, the `ssh_key_name` field in `vars/droplet.yml` must be unique per user.
* Real-time logging really only works well if the script being run takes a long time to complete and outputs a large amount of data to stdout.  As of now, there doesn't seem to be a way to increase the log output rate, but this may change in the future.
