#!/bin/bash

set -e

# sudo apt-get install -y amazon-cloudwatch-agent

sudo wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

rm ./amazon-cloudwatch-agent.deb

sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc

cat <<EOF | sudo tee "/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json" > /dev/null
{
  "metrics": {
    "namespace": "WebAppMetrics",
    "metrics_collected": {
      "statsd": {
        "service_address": ":8125",
        "metrics_collection_interval": 60,
        "metrics_aggregation_interval": 300
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/webapp.log",
            "log_group_name": "Webapp_ApplicationLog",
            "log_stream_name": "webapp_application_log",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          }
        ]
      }
    }
  }
}

EOF

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

sudo systemctl enable amazon-cloudwatch-agent

sudo touch /var/log/webapp.log

sudo chown csye6225:csye6225 /var/log/webapp.log

sudo chmod 664 /var/log/webapp.log
