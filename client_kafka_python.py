# coding: utf-8
# Copyright (C) zhongjie luo <l.zhjie@qq.com>
import datetime, os, sys
from db_bench.DbBench import DbConnection, multi_process_bench, Options, Option, Data
from kafka import KafkaProducer, KafkaConsumer, TopicPartition

kafka_options = list(Options.options)
kafka_options.append(Option("partition", "-P", 0))
kafka_options.append(Option("file", "-f", ".".join(os.path.abspath(__file__).split(".")[:-1]) + ".py"))
kafka_options.append(Option("length", "-l", 0))


class KafkaMsg(Data):
    def __init__(self, size, range_l=10000, options=None):
        super(KafkaMsg, self).__init__(size, range_l, options)
        length = options.get("length", 0)
        if length > 0:
            prefix = "-" * (length - 1)
            self.lines = ["%s%d" % (prefix, i) for i in range(10)]
        else:
            with open(options.get("file"), "r") as fp:
                self.lines = fp.readlines()
        self.size = len(self.lines)
        self.key = options.get("tag", str(datetime.datetime.now())) + " " + str(range_l) + " "

    def hook_get_key_and_value(self, index):
        return (self.key + str(index), self.lines[index % self.size])


class KafkaPython(DbConnection):
    def __init__(self, options):
        super(KafkaPython, self).__init__(options)
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
        self.__producer = KafkaProducer(bootstrap_servers=self.host)
        self.__consumer = KafkaConsumer(bootstrap_servers=self.host,
                                        group_id='client_kafka_benchmark',
                                        consumer_timeout_ms=1000)
        # self.__consumer.subscribe([self.__topic])
        partition = TopicPartition(self.__topic, self.__partition)
        self.__consumer.assign([partition])
        self.__consumer.seek_to_end(partition)
        # module bug, must request once at least, otherwise search fail
        self.__consumer.position(partition)

    def __set_up(self):
        try:
            for msg in self.__consumer:
                pass
                # print msg.value
        except:
            pass

    def disconnect(self):
        self.__producer = None
        self.__consumer = None

    @DbConnection.benchmark(u"生产")
    def producer(self, record):
        (k, v), index, last_index = record
        v = str(v)
        try:
            self.__producer.send(self.__topic, v)
        except (SystemExit, KeyboardInterrupt):
            raise SystemExit()
        except:
            self.__producer.flush()
            self.__producer.send(self.__topic, v)
        if index == last_index:
            self.__producer.flush()
        if self.__debug:
            print("++ " + v)
        return True

    @DbConnection.benchmark(u"消费")
    def consumer(self, record):
        k, v = record[0]
        v = str(v)
        if self.__consumer_interrupt:
            return False
        try:
            msg = next(self.__consumer)
        except (SystemExit, KeyboardInterrupt):
            raise SystemExit()
        except:
            print("timeout")
            self.__consumer_interrupt = True
            return False
        if len(msg.value) == 0:
            if self.quiet:
                print("msg.error, offset:" + str(msg.offset))
            self.__consumer_interrupt = True
            return False
        if self.__debug:
            print("--%d %s" % (msg.offset, msg.value))
        if v != msg.value:
            if not self.__debug:
                print("--%d %s" % (msg.offset, msg.value))
            if self.quiet:
                print("mismatch, mine:%s" % (v))
            self.__consumer_interrupt = True
            return False
        return True


if __name__ == "__main__":
    option = Options(kafka_options)
    option.set("port", 9092)
    if option.parse_option() is False:
        exit(100)
    # option.set("processor_num", 1)
    print(option)
    result = multi_process_bench(option, KafkaPython, KafkaMsg)
    # print result
