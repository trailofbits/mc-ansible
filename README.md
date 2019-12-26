# Manticore-Ansible

An Ansible script to automatically provision manticore in the cloud

## Actual documentation

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


