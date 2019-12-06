import sys
import yaml
import os
import subprocess
import paramiko
import os.path
from os import path

cloud = sys.argv[2].split('.')[0][-2:]
ip='99.99.99.2'
port=22
username='root'
password=''
print(cloud)

with open("/root/Migration-as-a-Service-2.0/etc/" + str(sys.argv[1]) + "/" + str(sys.argv[2]), 'r') as file:
    yaml_content = yaml.safe_load(file)

c1_pid = ''
for ns in yaml_content["Namespace"]:
    
    con_ns = ns["name"]
    print (con_ns)
    if cloud == "c2":
      print("In paramiko")
      ssh=paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(ip,port,username,password)
      
      cmd = "docker inspect -f '{{.State.Pid}}' " + str(con_ns)
      stdin,stdout,stderr=ssh.exec_command(cmd)
      outlines=stdout.readlines()
      c1_pid=''.join(outlines).rstrip()
      cmd1 = "ln -s /proc/" + str(c1_pid) + "/ns/net /var/run/netns/" + str(c1_pid)
      stdin,stdout,stderr=ssh.exec_command(cmd1)
      outlines1=stdout.readlines()
      ln_out=''.join(outlines1).rstrip()
      print("PID:", c1_pid)
    else:
      c1_pid = subprocess.Popen("docker inspect -f '{{.State.Pid}}' " + str(con_ns), shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
      print (c1_pid)
      fpath = "/var/run/netns/" + str(c1_pid)
      if not path.exists(fpath):
        os.system("ln -s /proc/" + str(c1_pid) + "/ns/net /var/run/netns/" + str(c1_pid))

    pid = {}
    pid = {'pid': c1_pid}
    ns.update(pid)
    yaml_content.update(ns)
    #print (yaml_content)

for sub in yaml_content["Subnet"]:
    con_sub = sub["ns_name"]
    print(con_sub)
    if cloud == "c2":
      print("In paramiko")
      ssh=paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(ip,port,username,password)
      
      cmd = "docker inspect -f '{{.State.Pid}}' " + str(con_sub)
      stdin,stdout,stderr=ssh.exec_command(cmd)
      outlines=stdout.readlines()
      s1_pid=''.join(outlines).rstrip()
      cmd1 = "ln -s /proc/" + str(s1_pid) + "/ns/net /var/run/netns/" + str(s1_pid)
      stdin,stdout,stderr=ssh.exec_command(cmd1)
      outlines1=stdout.readlines()
      ln_out=''.join(outlines1).rstrip()
      print("PID:", s1_pid)
    else:
      s1_pid = subprocess.Popen("docker inspect -f '{{.State.Pid}}' " + str(con_sub), shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
      print (s1_pid)
      fpath = "/var/run/netns/" + str(s1_pid)
      if not path.exists(fpath):
        os.system("ln -s /proc/" + str(s1_pid) + "/ns/net /var/run/netns/" + str(s1_pid))
  
    for vm_no, VM in enumerate(sub["vms"]):
      print(VM["name"])
      if cloud == "c2":
        print("In paramiko")
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,password)
        
        cmd2 = "docker inspect -f '{{.State.Pid}}' " + str(VM["name"])
        stdin,stdout,stderr=ssh.exec_command(cmd2)
        outlines2=stdout.readlines()
        con_pid=''.join(outlines2).rstrip()
        cmd3 = "ln -s /proc/" + str(con_pid) + "/ns/net /var/run/netns/" + str(con_pid)
        stdin,stdout,stderr=ssh.exec_command(cmd3)
        outlines3=stdout.readlines()
        con_out=''.join(outlines3).rstrip()
        print ("Con PID: ", con_pid)
      
      else:
        con_pid = subprocess.Popen("docker inspect -f '{{.State.Pid}}' " + str(VM["name"]), shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
        print ("Con PID:", con_pid)
       
      vm_pid = {}
      tenant_vm_pid = {}
      vm_pid = {'vm_pid': con_pid}
      VM.update(vm_pid)
      print(VM)
    
    pid = {}
    tenant_pid = {}
    pid = {'pid': s1_pid}
    tenant_pid = {'tenant_ns_pid': c1_pid}
    sub["tenant_ns"][0].update(tenant_pid)
    sub.update(pid)
    yaml_content.update(sub)


with open("/root/Migration-as-a-Service-2.0/etc/" + str(sys.argv[1]) + "/" + str(sys.argv[2]), 'w') as file:
    doc = yaml.dump(yaml_content, file, default_flow_style=False)
