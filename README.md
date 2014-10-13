docker-tester
=============

A simple tool to run automated tests on a fleet of docker images.
The code assumes the following:

1. boot2docker is installed and in the path, and hosts the docker server
2. the boot2docker image has a "current" snapshot (to cut down boot time)
3. an Apache server runs on the host, serving bashcheck
  * Bashcheck from [its github repo](https://github.com/hannob/bashcheck)

NOTE: this script **only** process the LATEST tag, and only images that
do have the tag.
