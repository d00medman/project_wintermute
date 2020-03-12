from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
import json

# TODO: bring the topic list in here

class KafkaNexus:

    def __init__(self, stream_from, stream_to):
        self.stream_from = stream_from
        self.stream_to = stream_to

        auto_offset_reset = 'earliest' if stream_from == 'emulator_to_data_set' else 'latest'

        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.consumer = KafkaConsumer(self.stream_from, auto_offset_reset=auto_offset_reset)

        print(f'Kafka nexus streaming messages from {self.stream_from} and receiving messages from {self.stream_to}')

    # TODO: maybe this can be passed into the consumer as the value_deserializer param?
    def decode_and_normalize_message(self, message):
        decoded_message = message.value.decode('utf-8').replace(']', '').replace('[', '')
        return [int(i) for i in decoded_message.split(",")]

    def write_message_to_stream(self, message):
        self.producer.send(self.stream_to, json.dumps(message))


def purge_topic(topic_name):
    admin_client = KafkaAdminClient()
    print(f'clearing messages from {topic_name}')
    admin_client.delete_topics(topic_name)
    admin_client.create_topics(topic_name)
    admin_client.close()



if __name__ == "__main__":
    nexus = KafkaNexus('emulator_to_data_set', 'n/a')

    # resetting computer purges topic?
    count = 0
    for message in nexus.consumer:
        count += 1
        print(f'message {count} on queue')
        # if count % 14 == 0:
        #     print(message.value)

    # print(f'{count} total messages on {nexus.stream_from}')


