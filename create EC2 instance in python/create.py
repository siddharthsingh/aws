import boto3
import time
from botocore.exceptions import ClientError


'''

Don't store aws_access_key_id and aws_secret_access_key here(in source file). 
If you are running this on AWS EC2 use roles instead of these values.
If you are running this somewhere else keep credentials in a credential file or environment variable.
Don't store your credentials on Github.

'''

ec2 = boto3.resource('ec2', region_name = 'us-east-1', aws_access_key_id = 'xxxxxxxxxxxxx' ,aws_secret_access_key = 'xxxxxxxxxxxxxxxxxxxxxx')

client = boto3.client('ec2', region_name='us-east-1',aws_access_key_id = 'xxxxxxxxx' ,aws_secret_access_key = 'xxxxxxxxxxxxx')


# searching for image ids
# to see filters or more details about the function go to
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_images
response = client.describe_images(Owners=['amazon'],
                                  Filters=[
                                      {
                                          'Name': 'name',
                                          'Values': [
                                              'amzn2-ami-hvm*',
                                          ]
                                      },
                                    {
                                          'Name': 'description',
                                          'Values': [
                                              'Amazon Linux 2 AMI*',
                                          ]
                                      },
                                    {
                                          'Name': 'block-device-mapping.volume-type',
                                          'Values': [
                                              'gp2',
                                          ]
                                      },
                                  ],
                                  )

for ami in response['Images']:
  print(ami)

ami_id = response['Images'][0]['ImageId']

#check if security group exists
try:
    all_sg = ec2.security_groups.all()
    security_group_found = False
    security_group_id = ''
    for sg in all_sg:
            if sg.group_name == 'testgroup':
                    security_group_found = True
                    security_group_id = sg._id
                    print('security group already present')
                    rule_found = False
                    for rule in sg.ip_permissions:
                          if rule['FromPort'] == 22 and rule['ToPort'] == 22 and rule['IpRanges'][0]['CidrIp'] == '0.0.0.0/0' and rule['IpProtocol'] == 'tcp':
                              print('security group has ssh port open')
                              rule_found = True
                              break
                    if not rule_found:
                        sg.authorize_ingress(IpProtocol="TCP",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)

    if not security_group_found:
            #create security group
            mysg = ec2.create_security_group(GroupName="testgroup",Description='testme')
            mysg.authorize_ingress(IpProtocol="TCP",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
            security_group_id = mysg._id
            print('security group created')

    # check if the user has SSH key
    keys = ec2.key_pairs.all()

    ssh_keys = []
    print('SSH Keys present: ')
    for key in keys:
        ssh_keys.append(key._name)
        print(key._name)

    print('Do you have any of these SSH keys?')

    while 1:
        input_value = input('Yes/No')
        if input_value.lower() in ['yes','no']:
            break
        else:
            print('invalid input')

    ssh_key_to_use = ''
    if input_value.lower() == 'yes':
        while 1:
            input_value = input('Enter the name of key file you want to associate with the new instance')
            if input_value in ssh_keys:
                ssh_key_to_use = input_value
                break
            else:
                print('invalid input')

    if input_value.lower() == 'no':
        while 1:
            input_value = input('Enter the name of key file you want to associate with the new instance')
            if input_value not in ssh_keys:
                ssh_key_to_use = input_value
                break
            else:
                print('Key with this name already exists. Use a new name ')
        #create a ssh key
        response = ec2.create_key_pair(KeyName=ssh_key_to_use)
        # save response.key_material
        with open(ssh_key_to_use+'.pem', 'w') as out:
            out.write(response.key_material)
        print('Key saved to current folder')
        print('If you are using linux/ubuntu use pem file to ssh into the new instance. '
              'Before SSHing into the instance, change the permission of the sshkey file to 400 (chmod 400 file.pem)')
        print('if you are using Windows, generate the ppk wile with puttygen')


    '''
    
    You can use UserData parameter to run the commands that you want to run as soon as the ec2 instance starts
    This can be used to set up a http server.
    To host your website on the new EC2 created, run the commands to install http server and 
    download the complete website code from S3.
    
    '''

    user_data = '''
    #!/bin/bash
    yum update -y
    amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
    yum install -y httpd mariadb-server
    systemctl start httpd
    systemctl enable httpd

    '''


    '''
    
    IamInstanceProfile is used to assign roles to your EC2 instances.
    For example you want to connect to a RDS from your newly launched EC2 instance, if you assign 
    a role to the EC2 which has a permission to interact with your RDS instance you won't have to save the credentials
    of the RDS in the new EC2. 
    
    '''

    instance = ec2.create_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=ssh_key_to_use,
        SecurityGroupIds=[security_group_id],
        # UserData=user_data,
        # IamInstanceProfile={
        #     'Name': 'ec2-full-access'
        # },
        )

    id = instance[0].id
    region = instance[0].placement['AvailabilityZone'][:-1]
    created = False
    public_ip = ''
    instance_id = ''

    while not created:
            instances = ec2.instances.filter(
                    Filters=[{'Name': 'instance-id', 'Values': [id]}])

            for instance in instances:
                    if instance.state['Name'] == 'pending':
                            print('Creation of instance is pending. please wait...')
                            time.sleep(3)
                            continue
                    public_ip = instance.public_ip_address
                    instance_id = instance.id
                    print('\n\ninstance created! Public Ip address: '+ instance.public_ip_address)
                    print('\nInstance region is '+ region)
                    print('Instance Id is : '+ instance_id)
                    created = True
                    break


    print('\nssh into the instance using the key file : '+ssh_key_to_use)
    print('ssh -i '+ssh_key_to_use+'.pem ec2-user@'+public_ip)



#     terminate instances
    ec2.instances.filter(
        Filters=[{'Name': 'instance-id', 'Values': [instance_id]}]).terminate()
    print('Terminating the instance')

except ClientError as ce:
    # auth failure, invalid ami id etc
    print(ce)
except Exception as e:
    print(e)
