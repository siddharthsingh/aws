Creating EC2 instance with AWS CLI
===

About
---

The AWS Command Line Interface (CLI) is a unified tool to manage your AWS services. With just one tool to download and configure, you can control multiple AWS services from the command line and automate them through scripts.

In this post, I will show you how to create an EC2 instance using AWS CLI. The process of creating EC2 with AWS CLI can be divided into the following major parts:


1.	Getting access key and secret access key
2. Installing and configuring AWS CLI
3. Create security group 
4. Create a key pair and change its permissions
5. Creating EC2 instance
6. Terminating EC2

Getting access key and secret access key
---

1. Go to AWS console home and select IAM
2. From left navigation bar select users
3. Click on add user button on top 
4. Enter the name of the user and in the access type select Programmatic access
5. Click on permissions button on the bottom right
6. Click on create group 
7. Enter the name of the group 
8. Select the permission you want to give to this user. For creating EC2 give it AmazonEC2FullAccess permission
9. Click on review and then create user
10. The new user will be creates and it will show you the access key ID and secret access key. Copy both of these somewhere as we would need this later to configure AWS CLI.


Installing and configuring AWS CLI
---

1. AWS CLI can be installed using pip. Run the following command to install it: pip3 install awscli
2. After it gets installed we need to configure it. To do that run the following command:  aws configure
3. Enter the AWS Access Key ID and the AWS Secret Access Key you got earlier.
4. Enter the Default region name according to you preference. Here is the list of regions. You can leave this blank if you want although if you do so you will have to provide the region input in every command.
5. Enter the Default output format. The AWS CLI supports three different output formats:JSON (json), Tab-delimited text (text), ASCII-formatted table (table)


Create security group 
---
1. Execute the following commands to create a security group that allows ssh connection(port 22).

```
aws ec2 create-security-group --group-name EC2SecurityGroup --description "Security Group for EC2 instances to allow port 22"

aws ec2 authorize-security-group-ingress --group-name EC2SecurityGroup --protocol tcp --port 22 --cidr 0.0.0.0/0
```

Create a key pair and setting its permissions
---
1. For sshing into the new EC2 we create we need ssh key file. Execute the following commands to create a new ssh key file.

```
aws ec2 create-key-pair --key-name MyKeyPair3 --query 'KeyMaterial' --output text --region us-west-2 > MyKeyPair3.pem
```
2. We need to change the permission of the key file we just created. To do that execute the following command:

```          
chmod 600 MyKeyPair3.pem
```

Creating an EC2 instance
---
Use the following command to create an EC2 instance:

```
aws ec2 run-instances --region us-west-2 --image-id  ami-32d8124a --key-name MyKeyPair3 --security-group-ids sg-fss3e980  --instance-type t2.micro --placement AvailabilityZone=us-west-2b --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=EC2NAME}]'
```

To get the image id run the following command:

```
aws ec2 describe-images --region us-west-2 
```

This would give a very large output so you may want to use it with grep

'ResourceType=instance,Tags=[{Key=Name,Value=EC2NAME}]'  This part sets the name of your new EC2 instance

The New EC2 will take a few minutes to create after which you can ssh into it using the key file you generated earlier.

Terminating your EC2
---
Run the following command to terminate your EC2:

```
aws ec2 terminate-instances --instance-id i-0xxxxxxxxxxxxxxx
```