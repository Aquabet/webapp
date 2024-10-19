packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0, < 2.0.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "source_ami" {
  type    = string
  default = "ami-04dd23e62ed049936"
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "subnet_id" {
  type    = string
  default = "subnet-08e9d10c24383023e"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "security_group_id" {
  type    = string
  default = "sg-0d3b0376297fa6113"
}

source "amazon-ebs" "my-ami" {
  region          = var.aws_region
  ami_name        = "csye6225_${formatdate("YYYY_MM_DD_HH_mm", timestamp())}"
  ami_description = "CSYE6225 AMI"
  profile         = "dev"
  ami_users       = []
  ami_regions = [
    "us-west-2",
  ]

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }

  instance_type     = var.instance_type
  source_ami        = var.source_ami
  ssh_username      = var.ssh_username
  subnet_id         = var.subnet_id
  security_group_id = var.security_group_id


  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
  }
}

build {
  sources = [
    "source.amazon-ebs.my-ami",
  ]

  provisioner "file" {
    source      = "./webapp.zip"
    destination = "/tmp/webapp.zip"
  }

  provisioner "file" {
    source      = "./provisioners/webapp.service"
    destination = "/tmp/webapp.service"
  }

  provisioner "file" {
    source      = "./provisioners/db_config.yaml"
    destination = "/tmp/db_config.yaml"
  }

  provisioner "shell" {
    script = "./provisioners/updateOs.sh"
  }

  provisioner "shell" {
    script = "./provisioners/appDirSetup.sh"
  }

  provisioner "shell" {
    script = "./provisioners/appSetup.sh"
  }

  provisioner "shell" {
    script = "./provisioners/dbSetup.sh"
  }
}
