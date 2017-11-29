# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
from imports import *
from confluent_kafka import Consumer, TopicPartition
from client_kafka import kafka_options


class KafkaConsumer(DbConnection):
    def __init__(self, options):
        super(KafkaConsumer, self).__init__(options)
        self.__topic = self.table
        self.__consumer = None
        self.__offset = options.get("offset", 0)
        self.__partition = options.get("partition", 0)
        self.__debug = self.record_num < 100 and self.quiet
        if self.port != 9092:
            self.host += ":%d" % self.port

    def connect(self):
        self.__consumer = Consumer({'bootstrap.servers': self.host,
                                    'socket.blocking.max.ms': 10,
                                    'group.id': 'kafka_benchmark',
                                    'default.topic.config': {'auto.offset.reset': 'smallest'}
                                    })
        self.__consumer.assign([TopicPartition(self.__topic, self.__partition, self.__offset)])

    def disconnect(self):
        self.__consumer.close()

    def search(self, record):
        (k,v), index, last_index = record
        msg = self.__consumer.poll(5)
        if msg is None:
            raise RuntimeError("offset: " + str(self.__offset + index))
            return False
        if self.__debug:
            print("--%d %s"%(msg.offset(), msg.value()))
        return True

    def _warm_up(self, record):
        pass


if __name__ == "__main__":
    kafka_options.append(Option("offset", "O", 0))
    option = Options(kafka_options)
    option.set("port", 9092)
    option.set("processor_num", 1)
    if option.parse_option() is False:
        exit(100)
    print(option)
    try:
        multi_process_bench(option, KafkaConsumer, Data)
    except:
        print(sys.exc_info())
        exit(1000)
