#!/usr/bin/python3
""" Python wrapper built around supporting Manticore functionality"""

import argparse
import sys
import subprocess
import logging
import os
import time

def parse_arguments():
	parser = argparse.ArgumentParser(description="Wrapper around Manticore CLI")
	destination = parser.add_argument_group("destination flags (local, remote)")

	destination.add_argument(
		"--local",
		action="store_true"
	)

	destination.add_argument(
		"--remote",
		action="store_true"
	)

	parser.add_argument(
		"--playbook",
		type=str,
		default="digitalocean.yml",
		help="specify Ansible playbook"
	)

	parsed, other = parser.parse_known_args(sys.argv[1:])

	if not len(sys.argv[1:]) > 0:
		print("Error: argv must be nonempty")
		sys.exit(1)

	if parsed.local ^ parsed.remote != 1:
		print("Error: must specify exactly one of --remote or --local flags")
		sys.exit(1)

	return parsed, other

def main():
	parsed, other = parse_arguments()
	
	flags = [flag for flag in other if flag.startswith("--")]
	files = [file for file in other if not file.startswith("--")]

	process = None

	if len(files) == 0:
		print("Error: must specify script to run")
		sys.exit(1)

	if parsed.local:
		if not files[0].endswith(".py"):
			to_run = ["manticore"]
			to_run.extend([files[0]])
			to_run.extend(flags)
		else:
			to_run = ["python3"]
			to_run.extend([files[0]]) 

		process = subprocess.Popen(to_run)

	# Allows the user to prematurely kill the subprocess with KeyboardInterrupt

	elif parsed.remote:
		to_run = ["ansible-playbook"]
		to_run.append(parsed.playbook)
		to_run.append("--extra-vars")
		to_run.append("manticore_script={}".format(files[0]))
		process = subprocess.Popen(to_run)

	try:
		while process is not None and process.poll() is None:
			time.sleep(0.1)
	except KeyboardInterrupt:
		process.terminate()


if __name__ == "__main__":
	main()
