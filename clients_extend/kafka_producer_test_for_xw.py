# Copyright (C) zhongjie luo <l.zhjie@qq.com>
# coding: utf-8
from imports import *
from client_kafka import KafkaMsg, kafka_options
from confluent_kafka import Producer


class KafkaProducer(DbConnection):
    def __init__(self, options):
        super(KafkaProducer, self).__init__(options)
        self.__topic = self.table
        self.__partition = options.get("partition", 0)
        self.__producer = None
        self.__producer_interrupt = False
        if self.port != 9092:
            self.host += ":%d" % self.port

    def connect(self):
        self.__producer = Producer({'bootstrap.servers': self.host,
                                    'socket.blocking.max.ms': 10})

    def disconnect(self):
        self.__producer = None

    def insert(self, record):
        try:
            self.__producer.produce(self.__topic, record.value())
        except:
            self.__producer.flush()
        if record.is_tail():
            self.__producer.flush()
        return True


if __name__ == "__main__":
    option = Options(kafka_options)
    option.set("port", 9092)
    if option.parse_option() is False:
        exit(100)
    print(option)
    result = multi_process_bench(option, KafkaProducer, KafkaMsg)
    # print result
