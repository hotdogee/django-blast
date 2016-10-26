## Welcome to Ansible

It assumes VirtualBox and Vagrant are available.  

To run django-blast setup with Ansible you must be in a directory (the "launch" directory) that contains the following files:

- `setup.py`
- `setup.ym`l
- `vm.yml`
- `vagrantfix.sh`
- `pg_hba.conf`

To do that run the convenience script:

`copy.sh <launch-dir>`

Where `<launch-dir>` is the directory from which you will run `setup.py`. Files in `<launch-dir>` will be shared with the VM,
where it will be known as `/vagrant`.  

This will copy the above files and `dotcp.sh`, a utility to copy your dot files to the VM home
if they exist. To use, copy the dot files wanted to `<launch-dir>` and then from the VM `/vagrant` dir 
run `dotcp.sh`, to copy to the VMs vagrant home.  It will recognize: .profile .bashrc .vimrc and .inputrc.  

While you can run ansible-playbook directly, for simplicity it is best to use the python wrapper *`setup.py`*, 
which calls *ansible-playbook* with the wanted flags and arguments.

Running time is approximately 20 minutes, including VM creation.

This is the usage of `setup.py`:

    setup.py

       host   = system where you run this command.
       target = VM to create or remote system where to setup django-blast.

       Installs django-blast project in target system

       Usage:

         setup.py [-a/-add <ip-addr>] [-i/--inv <inv-file>] [-r/--repo  <repo>] \
                  [-u/--user <user-name>] [-v/--vm <vm-name>] <target>

       target must be defined in the Ansible inventory file and it must be a single
       system, not a system group, because IP addresses are assigned singly. 

       If you create only one VM there is no need to specify the -a <ap-addr>
       option, unless the default vagrant address is already in use.  You can
       check by looking in the Vagrant file created in the current directory.
       after setup.py runs.

       If you want to create a second or more VMs then chose a new IP address
       within the range of other VMs already created, and pass it to setup.py
       with the -a <ip-addr> option.

       Add /etc/host entries for target, if inventory uses target names,
       or add the new IP address instead.

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
       directory of the target. Default: clone a fresh repo.

       If the -u/--user <user-name> option and argument are present,
       it uses <user-name> as the user in the target system.
       If creating a new VM, (-v) sets <user-name> automatically to 'vagrant'.
       Default: current user name.

       If the -v/--vm <vm-name>  option and argument are present,
       it creates a CentOS VM into which to do the setup.

       Options -v and -u are mutually exclusive.
       Options -a and -v are mutually inclusive.


First steps:

    # Copy inventory file to default dir.
    sudo cp hosts /etc/ansible

This is the default dir, it can be any dir but then you
have to tell ansible where it is with the -i option (ansible -i <path>) 

    # On OS X with homebrew installed Ansible, use this command:
    sudo cp hosts /usr/local/etc/ansible

Ad hoc command line is just: 

    ansible <host_from_inventory_file> -u <user_if_different> -m <module_name>  -a "<args_if_any>"  

man page: http://linux.die.net/man/1/ansible

To run a play book, ours in particular: 

    ansible-playbook -e"vm=<vm-name> target=<target>  setup.yml  

To get debug output: 

    ansible-playbook -vvv -e"vm=<vm-name> target=<target>  setup.yml  

man page: http://linux.die.net/man/1/ansible-playbook

