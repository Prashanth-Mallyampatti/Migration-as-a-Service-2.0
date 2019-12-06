import sys
import os
import subprocess
import yaml
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import paramiko

logging.basicConfig()

ip = '99.99.99.2'
port = 22
username = 'root'
password = ''

def polling():
  #print ("polling")
  f = open("/root/Migration-as-a-Service-2.0/etc/migrating.txt")
  is_migrating = f.read()

  #print (is_migrating)

  if is_migrating.rstrip() == "0":
    with open("/root/Migration-as-a-Service-2.0/src/northbound/config_files/infrastructure/" + str(sys.argv[1]) + ".yml", 'r') as file:
      main_yaml_content = yaml.safe_load(file)
      #print (main_yaml_content)

      #print (main_yaml_content["MISC"])

      ####################### Polling in cloud 1 ############################
      
      print ("\n\nPolling local containers")
  
      with open("/root/Migration-as-a-Service-2.0/etc/" + str(sys.argv[1]) + "/" + str(sys.argv[1]) + "c1.yml", 'r') as file:
        yaml_content = yaml.safe_load(file)

      #print (yaml_content)

      containers = subprocess.Popen("docker ps --all --format '{{.Names}}'", shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
      #print (containers)
      #print (containers.splitlines())

      for line in iter(containers.splitlines()):
        #print (line.rstrip())
        pid = subprocess.Popen("docker inspect --format '{{.State.Pid}}' " + str(line.rstrip()), shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
        #print ("printing pid")
        #print(pid)
        if pid is "0":
          for ns in yaml_content["Namespace"]:
            #print (ns["name"])
            if str(line.rstrip()) == str(ns["name"]):
              print (str(line.strip()) + " has stopped")
              print ("starting container " + str(line.strip()))
              exit_status = os.system("docker start " + str(line.rstrip()))
              break
          for sub in yaml_content["Subnet"]:
            if str(line.rstrip()) == str(sub["ns_name"]):
              print (str(line.strip()) + " has stopped")
              print ("starting conatiner " + str(line.strip()))
              exit_status = os.system("docker start " + str(line.rstrip()))
              break
            #print (sub["vms"])
            for vm in sub["vms"]:
              #print (vm["name"])
              if str(line.rstrip()) == str(vm["name"]):
                print (str(line.strip()) + " has stopped")
                print ("starting container " + str(line.strip()))
                exit_status = os.system("docker start " + str(line.rstrip()))
                break


      ####################### Polling in cloud 2 ############################

      print ("\n\nPolling remote containers")

      with open("/root/Migration-as-a-Service-2.0/etc/" + str(sys.argv[1]) + "/" + str(sys.argv[1]) + "c2.yml", 'r') as file:
        yaml_content = yaml.safe_load(file)

      #print (yaml_content)

      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(ip, port, username, password)

      get_all_containers = "docker ps --all --format '{{.Names}}'"
      stdin, stdout, stderr = ssh.exec_command(get_all_containers)
      containers = stdout.readlines()
      #print (containers)

      for line in containers:
        #print (line.strip())
        get_pid = "docker inspect --format '{{.State.Pid}}' " + str(line.strip())
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(get_pid)
        pid = stdout.readlines()
        #print (pid.readlines())
        pid = "".join(pid).strip()
        #print ("printing pid")
        #print(pid)
        if pid == "0":
          for ns in yaml_content["Namespace"]:
            #print (ns["name"])
            if str(line.strip()) == str(ns["name"]):
              print (str(line.strip()) + " has stopped")
              print ("starting container " + str(line.strip()))
              start_docker = "docker start " + str(line.strip())
              stdin, stdout, stderr = ssh.exec_command(start_docker)
              break
          for sub in yaml_content["Subnet"]:
            if str(line.strip()) == str(sub["ns_name"]):
              print (str(line.strip()) + " has stopped")
              print ("starting conatiner " + str(line.strip()))
              #exit_status = os.system("docker start " + str(line.rstrip()))
              start_docker = "docker start " + str(line.strip())
              stdin, stdout, stderr = ssh.exec_command(start_docker)
              break
            #print (sub["vms"])
            for vm in sub["vms"]:
              #print (vm["name"])
              if str(line.strip()) == str(vm["name"]):
                print (str(line.strip()) + " has stopped")
                print ("starting container " + str(vm))
                #exit_status = os.system("docker start " + str(line.rstrip()))
                start_docker = "docker start " + str(line.strip())
                stdin, stdout, stderr = ssh.exec_command(start_docker)
                break

print ("polling for every 10 seconds")
scheduler = BlockingScheduler()
scheduler.add_job(polling, 'interval', seconds=10)
scheduler.start()
