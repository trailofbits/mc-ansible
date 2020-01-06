#!/usr/bin/python3
""" Python wrapper built around supporting Manticore functionality"""

import argparse
import sys
import subprocess
import logging

def process_args(args):
	if args["local"] is None and args["remote"] is None: 
		print("Must specify whether task should be run locally or remotely")

	else if args["local"] is not None and args["remote"] is not None:
		print("Cannot specify both remote and local simultaneously!") 

	else if args["remote"]:
		subprocess.

def parse_arguments():
	parser = argparse.ArgumentParser(description="Specify remote or local Manticore run")
	parser.add_argument('--local', help="Runs a Manticore job locally", action="store")
	parser.add_argument('--remote', help="Runs a Manticore job on a remote instance", action="store")
	parser.add_argument('--workdir', nargs='?', const="./", help="Specify the working directory for Manticore job")
	args = vars(parser.parse_args())

def main():
	args = parse_arguments()

	

	