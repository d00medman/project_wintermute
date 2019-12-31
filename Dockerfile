FROM ubuntu:18.04

#RUN apt-get update && apt-get install -y \
#    aufs-tools \
#    automake \
#    build-essential \
#    curl \
#    dpkg-sig \
#    libcap-dev \
#    libsqlite3-dev \
#    mercurial \
#    reprepro \
#    ruby1.9.1 \
 #&& rm -rf /var/lib/apt/lists/*

# import wintermute
#COPY ./wintermute_prototype /wintermute_prototype


# set up nintaco - going to do this last due to difficulty presented by activating program server
FROM openjdk:7
COPY ./nintaco /nintaco
# RUN cd nintaco
RUN java -jar /nintaco/Nintaco.jar
# CMD["java", "-jar", "Nintaco.jar"]

# can load game from script, but am uncertain about how the program server can be launched w/o a gui, if at all.
# possible to load up emulator outside of container, enable program server, then move the emulator with open socket connection to the container?

# kafka setup

# launch nes environment with python 2.7
# set up and run venv
# run communication nexus in wintermute_amalgam

# deliver kickstart

# At least two connections 9998 - program server | 9092: kafka
