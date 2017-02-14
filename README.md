<!---
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
--->
Apache CloudStack EC2stack
==========================

**An EC2 Compatibility Interface For Apache CloudStack**

[![Build Status](https://travis-ci.org/apache/cloudstack-ec2stack.svg?branch=master)](https://travis-ci.org/apache/cloudstack-ec2stack)

Description
-----------

Apache [CloudStack](http://cloudstack.apache.org) is an open source software designed to deploy and manage large networks of virtual machines, as highly available, highly scalable Infrastructure as a Service (IaaS) cloud computing platform.

ec2stack takes Amazon EC2 API requests, maps these requests to the appropriate CloudStack API calls and parses the responses as required. This allows utilities created for the Amazon EC2 API to be used against Apache CloudStack.

Easy setup with [Docker](http://docker.com)
-------------------------------------------

The easiest way to run ec2stack is to use a docker container. Pull the image from docker hub.

    $ docker pull cloudstack/cloudstack-ec2stack

Run an interactive container and configure ec2stack for your CloudStack endpoint.
Be careful to use 0.0.0.0 as the bind address for ec2stack server.

    $ docker run -ti cloudstack/cloudstack-ec2stack ec2stack-configure

Commit the configured container into a new image specific to your cloud.

    $ docker commit <container id> ec2stack:yourcloud

Run an container with the ec2stack command

    $ docker run -d -p 5000:5000 ec2stack:yourcloud ec2stack
    
Setup on [CentOS 7](https://www.centos.org/) or [Fedora](https://getfedora.org/)
-------------------------------------------

Install python-pip and git.

    $ yum install python python-devel python-pip git
    
Upgrade requests package.

    $ pip install --upgrade requests
    
Clone this repository.

    $ git clone https://github.com/apache/cloudstack-ec2stack.git
    $ cd cloudstack-ec2stack

Proceed with installation.

    $ python ./setup.py install

Configure ec2stack for your CloudStack endpoint.

    $ ec2stack-configure

Run ec2stack

    $ ec2stack

... Or in debug mode

    $ ec2stack -d DEBUG
    
Setup on [Debian 8](https://www.debian.org/) or [Ubuntu >=14.04](https://www.ubuntu.com/)
-------------------------------------------

Install python-pip and git.

    $ apt-get update && apt-get install -y python python-dev python-pip git
    
Upgrade requests package.

    $ pip install --upgrade requests
    
Clone this repository.

    $ git clone https://github.com/apache/cloudstack-ec2stack.git
    $ cd cloudstack-ec2stack

Proceed with installation.

    $ python ./setup.py install

Configure ec2stack for your CloudStack endpoint.

    $ ec2stack-configure

Run ec2stack

    $ ec2stack

... Or in debug mode

    $ ec2stack -d DEBUG
    
Usage
-------------------------------------------

Register a user

    $ curl -d AWSSecretKey=yoursecretkey -d AWSAccessKeyId=yourapikey -d Action=RegisterSecretKey http://localhost:5000

This should return an xml response with the message "Successfully Registered"

On Ubuntu systems install _pip_ and _awscli_ like so:

    $ sudo apt-get install python-pip
    $ sudo pip install awscli

Configure the AWS cli by entreing your CloudStack cloud API keys, and the name of the zone. Set the signature version to be _v2_:

    $ aws configure
    $ aws configure set default.ec2.signature_version v2

You now just need to configure your aws cli and use the local ec2stack point:

    $ aws ec2 describe-images --endpoint=http://localhost:5000
    
For more usage information please see the [User Guide](https://github.com/apache/cloudstack-ec2stack/blob/master/USER.md).

Limitations
-----

**IMPORTANT**: Please note that the current version of ec2stack only supports AWS Signature Version 2 and therefore will NOT work with the current AWS CLI unless you explicitly tell it to use Version 2.  You can set the signature version for your default AWS CLI profile with:

    $ aws configure set default.ec2.signature_version v2

If you are using named profiles then you can set the version for the specific profile with:

    $ aws configure set profile.<your profile name>.ec2.signature_version v2

Both of the above commands will update your *~/.aws/config* file.
