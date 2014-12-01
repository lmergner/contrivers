# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
    config.vm.define "local" do |local|
        local.vm.box = "contrivers/debian-7.6"
        local.vm.network :forwarded_port, guest: 80, host: 8080
        local.vm.network "public_network", bridge: 'en0: Ethernet 1'
        local.ssh.forward_agent = true
        local.vm.synced_folder ".", "/vagrant", disabled: true
    end

    config.vm.define 'staging' do |staging|
        staging.vm.box = "aws"
        staging.vm.box_url = "https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box"
        staging.vm.synced_folder ".", "/vagrant", disabled: true
        staging.vm.provider :aws do |aws, override|
            aws.access_key_id = ENV["aws_access_key"]
            aws.secret_access_key = ENV["aws_secret_key"]
            aws.ami = "ami-5faca41a"  # Debian Wheezy
            aws.region = "us-west-1"
            aws.instance_type = "t1.micro"
            aws.security_groups = ["default", "web"]
            override.ssh.username = "admin"
            override.ssh.private_key_path = ENV["aws_key_file"]
        end
    end

    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "provisioning/site.yml"
        ansible.verbose = 'vvvv'
        ansible.sudo = true
        ansible.host_key_checking = false
        ansible.extra_vars = { 
            ansible_ssh_user: 'vagrant',
            ansible_connection: 'ssh',
            ansible_ssh_args: '-o ForwardAgent=yes'}
    end
end
