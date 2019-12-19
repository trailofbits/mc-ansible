# Manticore-Ansible

An Ansible script to automatically provision manticore in the cloud

## Actual documentation

### Initial setup

(Warning: very rough and experimental)

* Run `pip3 install ansible "dopy>=0.3.7"`
* Generate an ed25519 SSH key via `ssh-keygen -t ed25519`(stored in ~/.ssh/id_ed25519)
* Navigate to var/
* In droplet.yml, add DigitalOcean API key in commented section
* In ansible.yml, change the value of the commented variables to be as desired.
* Run `ansible-playbook -vvv digitalocean.yml`

### Tearing down the VM
* Run `ansible-playbook -vvv tear_down_instance.yml`


