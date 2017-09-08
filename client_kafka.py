# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import datetime, os
from db_bench.DbBench import DbConnection, multi_process_bench, Options, Option, Data
from confluent_kafka import Producer, Consumer, TopicPartition


kafka_options = list(Options.options)
kafka_options.append(Option("partition", "-P", 0))
kafka_options.append(Option("file", "-f", os.path.abspath(__file__).split(".")[0]+".py"))
kafka_options.append(Option("length", "-l", 0))


class KafkaMsg(Data):
    def __init__(self, size, range_l=10000, options=None):
        super(KafkaMsg, self).__init__(size, range_l, options)
        length = options.get("length", 0)
        if length > 0:
            prefix = "-" * (length-1)
            self.lines = ["%s%d"%(prefix,i) for i in range(10)]
        else:
            with open(options.get("file"), "r") as fp:
                self.lines = fp.readlines()
        self.size = len(self.lines)
        self.key = options.get("tag", str(datetime.datetime.now())) + " " + str(range_l) + " "

    def hook_get_key_and_value(self, index):
        return (self.key + str(index), self.lines[index % self.size])


class ConfluentKafka(DbConnection):
    def __init__(self, options):
        super(ConfluentKafka, self).__init__(options)
        self.__topic = self.table
        self.__partition = options.get("partition", 0)
        self.__producer = None
        self.__consumer = None
        self.__producer_interrupt = False
        self.__consumer_interrupt = False
        self.__debug = self.record_num < 100 and self.quiet
        if self.port != 9092:
            self.host += ":%d" % self.port

    def connect(self):
        # 不稳定，第一次操作耗时长
        self.__producer = Producer({'bootstrap.servers': self.host,
                                    'socket.blocking.max.ms': 10})
        self.__consumer = Consumer({'bootstrap.servers': self.host,
                                    'socket.blocking.max.ms': 10,
                                    'group.id': 'client_kafka_benchmark',
                                    'default.topic.config': {'auto.offset.reset': 'largest'}
                                    })
        self.__consumer.subscribe([self.__topic])
        # consumer offset to end
        while True:
            msg = self.__consumer.poll()
            if msg.error():
                if self.quiet:
                    print("start offset: %d" % (msg.offset()))
                break

    def disconnect(self):
        self.__producer = None
        self.__consumer.close()
        self.__consumer = None

    def insert(self, record):
        try:
            self.__producer.produce(self.__topic, record.value())
            if record.is_tail():
                self.__producer.flush()
        except:
            self.__producer.flush()
            self.__producer.produce(self.__topic, record.value())
        if self.__debug:
            print("++" + record.value())
        return True

    def search(self, record):
        if self.__consumer_interrupt:
            return False
        msg = self.__consumer.poll()
        if msg.error():
            if self.quiet:
                print("msg.error, offset:" + str(msg.offset()))
            self.__consumer_interrupt = True
            return False
        if self.__debug:
            print("--%d %s" % (msg.offset(), msg.value()))
        if record.value() != msg.value():
            if self.quiet:
                print("mismatch, mine:%s" %(record.value()))
            self.__consumer_interrupt = True
            return False
        return True


if __name__ == "__main__":
    option = Options(kafka_options)
    option.set("port", 9092)
    if option.parse_option() is False:
        exit(100)
    option.set("processor_num", 1)
    print(option)
    result = multi_process_bench(option, ConfluentKafka, KafkaMsg)
    # print result
