#!/usr/bin/python

for i in range(1,200):
    #print "curl -b cookies.txt -c cookies.txt -X POST --header \"Content-Type:application/json\" --data \"{\"firstName\":\"Bob\", \"lastName\":\"Smith\", \"email\":\"bob" +str(i)+ "@admin.gov\", \"newpassword\":\"supersecret\", \"role\": \"user\", \"username\": \"R2D2@i5k.org\", \"password\": \"demo\"}\" http://localhost:8085/apollo/user/createUser"

    #print "curl -b cookies.txt -c cookies.txt -X POST --header \"Content-Type:application/json\" --data \"{\"name\":\"GROUP_"+str(i)+"_USER\", \"username\": \"R2D2@i5k.org\", \"password\": \"demo\"}\" http://localhost:8085/apollo/group/createGroup"

    print "curl -b cookies.txt -c cookies.txt -X POST --header \"Content-Type:application/json\" --data \"{\"name\":\"GROUP_"+str(i)+"_USER\", \"username\": \"R2D2@i5k.org\", \"password\": \"demo\"}\" http://localhost:8085/apollo/group/deleteGroup"
