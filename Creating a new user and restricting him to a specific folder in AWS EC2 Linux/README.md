Creating a new user and restricting him to a specific folder in AWS EC2 Linux
===

Creating a new website? Need to give someone access to the website folder on your EC2 instance without giving him the complete access to your EC2? If the answer to that is yes you may find this blog helpful. 

I had to work on a website with my project partner when I thought I should use EC2 so that we both can collaborate as well as see the website live. So I needed to give access to my friend so that he can also work on the website, but at the same time, I didn't want him to get access to all the other folders that I had on EC2. 

The whole process can be divided into the following steps
---
1. Create a new group and user
2. Generating SSH keys to login to EC2 from SFTP
3. Connecting to EC2 as the new user using FileZilla.


Let's dig deeper to understand how each of these steps works. 

Create a new group and user
---

1. Start by creating a new group. We will add the user we create in the following steps to this group. Use the following code to create a new group.

```
sudo addgroup exchangefiles
```

2. Create the root directory for the group. After creating the directory we change the permissions of that directory. We set it to read and execute. You can set this according to your needs. All users in this group will be able to read and execute from this folder. The can write only in their specific folders.

```
sudo mkdir /var/www/GroupFolder/
sudo chmod g+rx /var/www/GroupFolder/
```

3. Now create another directory for the user. Give it write permission as well. Same as above you can give the permissions according to your needs. Also, You don't have to create two different directories, you can create just one directory and give it the permissions you need.

```
sudo mkdir -p /var/www/GroupFolder/files/
sudo chmod g+rwx /var/www/GroupFolder/files/
```

4. Assign both these directories to the group we created.
```
sudo chgrp -R exchangefiles /var/www/GroupFolder/
```

 5. Edit /etc/ssh/sshd_config and make sure to add the following at the end of the file:
``` 

  # Force the connection to use SFTP and chroot to the required directory.  
  ForceCommand internal-sftp  
  ChrootDirectory /var/www/GroupFolder/  
  # Disable tunneling, authentication agent, TCP and X11 forwarding.  
  PermitTunnel no  
  AllowAgentForwarding no  
  AllowTcpForwarding no  
  X11Forwarding no  

```








6. Now let's create a new user. 
```
sudo adduser -g exchangefiles obama 
```

If you get a command not found error It might be because your environment doesn't include the /usr/sbin directory that holds such system programs. The quick fix should be to use /usr/sbin/adduser instead of just adduser
Now that we have made the proper changes let's restart ssh so that it can reflect the changes.
sudo /sbin/service sshd restart

You are all set. You have created a new user and group and given the permission of the folder to that group. The user can connect only using SFTP protocol. You can use FileZilla for connecting using you the new user. When you log in you will be in the folder you created above. You cannot go out of that folder.

Generating SSH keys to login to EC2 from SFTP
---
Now for connecting to EC2 as the new user you first need to create the public and private ssh keys. The public ssh key will be in the home folder of the new user and you will download the private key on your system. You have to use this key file(permanent key) on FileZilla to connect to EC2.

1. Go to the home directory of the new user and execute the following commands to create a new folder and set permissions to it.
```
cd
mkdir .ssh
chmod 700 .ssh
```

2. Now create a file in .ssh and set its permissions
```
touch .ssh/authorized_keys
chmod 600 .ssh/authorized_keys
```

3. Now generate your public and private keys using the following command. replace username with the name of the new user that you created
```
ssh-keygen -f username
```

This will generate two files username and username.pub. username is your private key and username.pub is your public key.

4. Copy the public key, and then use the Linux cat command to paste the public key into the .ssh/authorized_keys file for the new user.
```
cat username.pub > .ssh/authorized_keys
```

5. Download the private key file to your local system. This will be used to login using SFTP. 

Connecting to EC2 as the new user using FileZilla.
---
1. Open FileZilla. Go to File->site manager->New Site. Enter the details here. The host is the public DNS of your EC2. leave the port empty, change the protocol to SFTP, set logon type to "key file", set the user to the new user that you created, browse to where you downloaded your private key and set it in "key file".


2. Click on connect


That's it, you have now configured your EC2 to give limited accedd to a user.