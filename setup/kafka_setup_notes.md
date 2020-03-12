using: https://timber.io/blog/hello-world-in-kafka-using-python/

1. install kafka (where? locally, within the wintermute_prototype repo?)
- download tar from link and un-tar using (what is un-tarring)? `tar -xzf kafka_2.11-1.1.0.tgz`
- `cd` into newly created directory (create directory locally): `cd kafka_2.11-1.1.0` (further commands in this tutorial from this point)

2. Start zookeeper (centralized service for a distributed environment like kafka) server
- `bin/zookeeper-server-start.sh config/zookeeper.properties`

3. Star Kafka server `bin/kafka-server-start.sh config/server.properties`

4. Kafka configuration commands:
Create kafka topics - `bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic <topic_names>`
List kafka topics `bin/kafka-topics.sh --list --zookeeper localhost:2181`
More details on a particular topic: `bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic sample`

5. Set up kafka producers consumers
5.1. if not installed already, run `pip install kafka-python` (kafka-venv relation as sketchy to me as all venv relations, could be source of problems)

Methodology that actually seems to work derived from [this article](https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-18-04)
- `su -l kafka` => logs me into my local kafka user
- once this is done, will see command line with `$` prompt:
- `~/kafka/bin/kafka-topics.sh --list --zookeeper localhost:2181` lists topics
- create topics
- `~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic amalgam_to_emulator`
- `~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic emulator_to_amalgam`
- `~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic emulator_to_dataset`
- `~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic emulator_to_harness`

first run
- `echo "created from command line" | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic amalgam_to_emulator > /dev/null` - sends message to tutorial topic, which I will be observing when spinning up server
then run
- `echo "0" | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic amalgam_to_emulator > /dev/null`
- `~/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic emulator_to_amalgam --from-beginning`

-`exit` closes shell session. exit does not delete topiocs

then, in wintermute_prototype, run nes environment


This is the Methodology which works i nthe hello world paradigm. Can read to and write from distinct kafka topics in the nes emulator environment

Does the terminal launched by the logon command need to be open for the streams to be open, or is this run passively in background?
Prospect of a quick setup & cleanup script?

Not kafka; tensorboard can be kickstarted with following command (probably worth putting into bash:

tensorboard --logdir=graph_logs20200125-135630/ --host localhost --port 8088