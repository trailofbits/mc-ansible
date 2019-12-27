# Manticore-Ansible

An Ansible script to automatically provision manticore in the cloud

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

* manticore_env: directory in which manticore scripts will be run
* manticore_script: script inside of manticore_env to run
* remote_uname: username on the droplet
* working_dir: current working directory on local machine
* logfile: log file of manticore script that will be saved under working_dir



### Initial setup

(Warning: very rough and experimental)

* Run `pip3 install ansible "dopy>=0.3.7"` (currently uses digital_ocean which is meant to only be compatible with python2, but with a bit of tweaking can be made compatible with python3.  Only other option is the digital_ocean_droplet module, but it has poor documentation and from what I've seen, is bug-ridden.)
* Generate an SSH key via `ssh-keygen -t <key_type_here>`(stored in ~/.ssh/)
* Define an environment variable `DO_TOKEN` that holds the DigitalOcean API token in plaintext; (e.g. on Ubuntu run `export DO_TOKEN=<your_api_key_in_hexadecimal>`)
* Navigate to `vars/`
* In droplet.yml, set the value of `droplet_ssh_key` to the path of the public key file (e.g. for an ed25519 key in `/.ssh/id_ed25519.pub`, set `droplet_ssh_key` to `"{{ lookup('file', lookup('env','HOME') + '/.ssh/id_ed25519.pub') }}")`
* In ansible.yml, change the value of the variables (droplet name, username, etc) to be as desired.
* Run `ansible-playbook -vvv digitalocean.yml`

### Tearing down the VM
* Run `ansible-playbook -vvv tear_down_instance.yml`

### Notes

* When provisioning and tearing down multiple instances, change the value of `droplet_name` in `vars/droplet.yml` to be the respective name of the instance to destroy.
* Sometimes if the SSH service on the droplet times out, a permission denied error will occur when re-running the `digitalocean.yml` script.  To solve this issue, run `ansible-playbook reset_ssh_key.yml -vv` to reset the SSH key on the server.
