import sys
import os
import subprocess
import yaml
#import logging
from apscheduler.schedulers.blocking import BlockingScheduler

#logging.basicConfig()

def polling():
  print ("polling")
  f = open("/root/Migration-as-a-Service-2.0/etc/migrating.txt")
  is_migrating = f.read()

  print (is_migrating)

  if is_migrating.rstrip() == "0":
    with open("/root/Migration-as-a-Service-2.0/src/northbound/config_files/infrastructure/" + str(sys.argv[1]) + ".yml", 'r') as file:
      main_yaml_content = yaml.safe_load(file)
      #print (main_yaml_content)

      #print (main_yaml_content["MISC"])

      with open("/root/Migration-as-a-Service-2.0/etc/" + str(sys.argv[1]) + "/" + str(sys.argv[1]) + "c1.yml", 'r') as file:
        yaml_content = yaml.safe_load(file)

      #print (yaml_content)

      containers = subprocess.Popen("docker ps --all --format '{{.Names}}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      print (containers.communicate())

      for line in iter(containers.stdout.readline,''):
        #print (line.rstrip())
        pid = subprocess.Popen("docker inspect --format '{{.State.Pid}}' " + str(line.rstrip()), shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
        #print ("printing pid")
        #print(pid)
        if pid is "0":
          for ns in yaml_content["Namespace"]:
            #print (ns["name"])
            if str(line.rstrip()) == str(ns["name"]):
              print ("starting namespace container")
              exit_status = os.system("docker start " + str(line.rstrip()))
              break
          for sub in yaml_content["Subnet"]:
            if str(line.rstrip()) == str(sub["ns_name"]):
              print ("starting subnet conatiner")
              exit_status = os.system("docker start " + str(line.rstrip()))
              break
            #print (sub["vms"])
            for vm in sub["vms"]:
              #print (vm["name"])
              print ("starting vm container")
              if str(line.rstrip()) == str(vm["name"]):
                exit_status = os.system("docker start " + str(line.rstrip()))
                break

print ("running for every 2 seconds")
scheduler = BlockingScheduler()
scheduler.add_job(polling, 'interval', seconds=2)
scheduler.start()
