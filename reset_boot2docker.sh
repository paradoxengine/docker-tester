#!/bin/bash
# A simple script to reset the status of the boot2docker vm
VBoxManage controlvm boot2docker-vm poweroff
VBoxManage snapshot boot2docker-vm restorecurrent
VBoxManage startvm boot2docker-vm
