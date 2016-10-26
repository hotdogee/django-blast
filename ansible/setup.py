#!/usr/bin/env python
'''
   setup.py

   Installs django-blast project in target system/s

   This script must be run from a directory that contains setup.yml, vm.yml, and vagrantfix.sh.

   host   = system where you run this command.
   target = VM created or remote system/s.

   Usage:

     setup.py [-a <ip-addr>] [-i/--inv <inv-file>] [-r/--repo  <repo>] [-v/--vm <vm-name>] \
              [-u/--user <user-name>] [-v/--vm <vm-name>] <target> ]

   target must be defined in the Ansible inventory file and it must be a single
   system, not a system group, since ip addresses are assigned singly.

   Add /etc/host entries for all hosts, if inventory uses target names.

   Creates a 'django-blast' directory in the remote user's home directory and
   makes it a virtual environment, places the django-blast project in it,
   and installs dependencies.

   if the -a/--addr <ip-addr> option and argument are present
   the new vm will use the given IP address.
   Default: as in the default Vagrantfile. (usually 192.168.33.10)
   This argument requires the -v <vm-name> argument to be present also.

   if the -i/--inv <inv-file> option and argument are present
   it passes to Ansible the <inv-file> file to use as inventory.
   Default: /etc/ansible/hosts

   if the -r/--repo <repo> option and argument are present
   it assumes <repo> is a directory, in the host system, containing the
   django-blast project, and it copies its contents into the django-blast
   directory/virtualenv of the new installation. Default: clone a fresh repo.

   If the -u/--user <user-name> option and argument are present,
   it uses <user-name> as the user in the target system/s.
   If creating a new VM, (-v) sets <user-name  automatically to 'vagrant'.
   Default: current user name.

   If the -v/--vm <vm-name>  option and argument are present,
   it creates a CentOS VM into which to do the setup.

   Options -v and -u are mutually exclusive.
   Options -a and -v are mutually inclusive.

'''

import os
import time
import argparse
import getpass

YML_FILE = 'setup.yml'
CMD = 'ansible-playbook -e'

def getDefaultAddr():
    '''  Get the default IP from Vagrantfile  '''
    addr = ''
    os.system("rm -f Vagrantfile")
    os.system("vagrant init bento/centos-6.7 > /dev/null ")
    with open('Vagrantfile') as p:
        for line in p:
            if line.startswith('  # config.vm.network "private_network", ip:'):
                addr = line.rstrip().split(' ')[6].replace('"','')
    os.system("rm -f Vagrantfile")
    return addr


def main():
    '''  Parse arguments and build Ansible command to call.  '''

    parser = argparse.ArgumentParser(description='Set up the django-blast project on remote system/s.')
    parser.add_argument('-a', '--addr', help='IP Address', nargs=1, dest='ip_addr', metavar='ip-addr')
    parser.add_argument('-i', '--inv', help='Inventory file', nargs=1, dest='inv_file', metavar='inv-file')
    parser.add_argument('-r', '--repo', help='Use project in <repo>>', nargs=1, dest='repo', metavar='repo')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--user', help='Target system/s user>', nargs=1, dest='user_name', metavar='user-name')
    group.add_argument('-v', '--vm', help='Create a VM named <vm-name>', nargs=1, dest='vm_name', metavar='vm-name')
    parser.add_argument('target', help='target system/s', nargs='+')

    args = parser.parse_args()

    arg_str = ''
    user    = ''

    if args.ip_addr:
        if args.vm_name:
            arg_str += 'addr=%s ' % args.ip_addr[0]
        else:
            parser.error('the -a <ip_addr> argument requires the -v <vm_name argument to be also specified')
    else:
        ip_addr = getDefaultAddr()
        if not ip_addr:
            print "Can't find default address in Vagrant file"
            exit(1)
        arg_str += 'addr=%s ' % ip_addr

    if args.inv_file:
        inv_file  = '-i %s ' % args.inv_file[0]
    else:
        inv_file  = ''

    if args.repo:
        arg_str += 'repo=%s ' % args.repo[0]

    if args.user_name:
        user = args.user_name[0]

    if args.vm_name:
        arg_str += 'vm=%s ' % args.vm_name[0]
        user = 'vagrant'

    arg_str += "target='%s' " % ' '.join(args.target)

    if not user:
        user = getpass.getuser()

    arg_str += 'user=%s' % user

    print "\nRunning ansible-playbook command..."
    print '\n%s "%s" %s %s' % (CMD, arg_str, inv_file, YML_FILE)
    time.sleep(5)
    os.system('%s "%s" %s %s' % (CMD, arg_str, inv_file, YML_FILE))


if __name__ == '__main__':
    try:
        print "\n"
        main()
    except KeyboardInterrupt:
        print '\nAborting... \n'

    exit(0)

