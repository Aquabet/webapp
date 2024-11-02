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

variable "demo_account_id" {
  type    = string
  default = "345594606247"
}

variable "device_name" {
  type    = string
  default = "/dev/sda1"
}

variable "ami_description" {
  type    = string
  default = "CSYE6225 AMI"
}

variable "ami_regions" {
  type    = list(string)
  default = ["us-west-2"]
}

variable "profile" {
  type    = string
  default = "dev"
}

variable "delay_seconds" {
  type    = number
  default = 120
}

variable "max_attempts" {
  type    = number
  default = 50
}

variable "volume_size" {
  type    = number
  default = 8
}

variable "volume_type" {
  type    = string
  default = "gp2"
}

source "amazon-ebs" "my-ami" {
  region          = var.aws_region
  ami_name        = "csye6225_${formatdate("YYYY_MM_DD_HH_mm", timestamp())}"
  ami_description = var.ami_description
  profile         = var.profile
  ami_users       = [var.demo_account_id]
  ami_regions     = var.ami_regions

  aws_polling {
    delay_seconds = var.delay_seconds
    max_attempts  = var.max_attempts
  }

  instance_type     = var.instance_type
  source_ami        = var.source_ami
  ssh_username      = var.ssh_username
  subnet_id         = var.subnet_id
  security_group_id = var.security_group_id


  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = var.device_name
    volume_size           = var.volume_size
    volume_type           = var.volume_type
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
    script = "./provisioners/cloudwatchSetup.sh"
  }
}
