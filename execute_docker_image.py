#!/usr/bin/python3
"""
Goes over a list of docker images, downloads them in a VM,
running boot2docker then downloads a script and executes
it on them. Filters out the results and saves them in a file.
In this version, both the address of the VM and of the script
are hardcoded on local IPs.
"""

from subprocess import Popen, PIPE, TimeoutExpired
import argparse
import datetime
import locale
import os
import psutil
import subprocess
import threading
import time

def resetVm():
  proc = Popen("./reset_boot2docker.sh", stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
  try:
    proc.wait(30)
  except TimeoutExpired:
    proc.kill()
    log('TIMEOUT reset boot2docker')
    for process in psutil.process_iter():
      if process.name == 'VirtualBox':
        process.kill()
    resetVm()
  time.sleep(2)
  log('END RESET boot2docker')


def getImageVulns(image):
  # Note that the IP was set by boot2docker.
  docker_env = {"DOCKER_HOST": "tcp://192.168.59.105:2375"}
  proc = Popen(["docker", "run", image, "/bin/bash", "-c",
		"apt-get update && apt-get install wget -y && wget http://192.168.59.3/bashcheck -O /tmp/bashcheck && chmod +x /tmp/bashcheck && /tmp/bashcheck"], env=docker_env, stdout=PIPE, stderr=PIPE)
  try:
    timeout = 60 * 20
    outs, errs = proc.communicate(timeout=timeout)
  except TimeoutExpired:
    log('TIMEOUT processing %s' % image)
    proc.kill()
    outs, errs = proc.communicate()
  vulns = []
  encoding = locale.getdefaultlocale()[1]
  for line in outs.splitlines():
    if 'Vulnerable' in line.decode(encoding):
      vulns.append(line.decode(encoding))
  return vulns

def log(message):
  now = datetime.datetime.now()
  print('[%s] %s' % (now, message))

parser = argparse.ArgumentParser(
    description='Tests shellshock on docker images (debian based ONLY).')

parser.add_argument('output_file', metavar='output_file',
		    help='File to write output to')
inputs = parser.add_mutually_exclusive_group(required=True)
inputs.add_argument('--image_file', metavar='image_file',
                   help='File to read a list of images from')
inputs.add_argument('--image', metavar='image',
		    help='A single image')
args = parser.parse_args()

with open(args.output_file, 'w') as output:
  images = []
  if args.image_file:
    with open(args.image_file, 'r') as image_file:
      for line in image_file:
        images.append(line)
  if args.image:
    images.append(args.image)

  image_counter = 0
  for image in images:
    image = image.strip().strip('/')  # removes images ending with /
    log('Processed %s images' % image_counter)
    image_counter += 1
    log('START RESET boot2docker')
    resetVm()    
    log('Sleeping 45 seconds to avoid triggering DOS protections')
    time.sleep(45)
    log('START TEST %s' % image)
    vulns = getImageVulns(image)
    encoding = locale.getdefaultlocale()[1]
    for vuln in vulns:
      log(vuln)
      # Output is in "CSV" format :-)
      output.write(image + ',' + vuln + '\n')
    output.flush()
    log('END TEST %s' % image)
