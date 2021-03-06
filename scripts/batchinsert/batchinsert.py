# 
import random
# pip install python-dateutil
from dateutil import parser as DateParse
import time
import sys

def unixtime(datestr):
    return int(DateParse.parse(datestr).timestamp())

# base class
class ValueGenerator:
    def __init__(self, **flags):
        self.flags = flags
        if hasattr(self, 'initialize'):
            self.initialize()

##########################################
# Generators
class ListGenerator(ValueGenerator):
    def adapt(self, v):
        self.v = v

    def __next__(self):
        return random.choice(self.v)

class RelatedDataSource:
    __generators = {}
    __header = None
    __lines = []
    __choice = None

    def __init__(self, filename):
        with open(filename, encoding='utf8') as file:
            self.__header = list(map(lambda x: x.strip(), file.readline().split(',')))

            for line in file.readlines():
                items = list(map(lambda x: x.strip(), line.split(',')))
                self.__lines.append(items)

    def get_index(self, field_name):
        index = 0
        while True:
            if self.__header[index] == field_name:
                return index
            index += 1
            if index >= len(self.__header):
                return -1
        return -1

    def get_lines(self):
        return self.__lines

    def get_generator(self, field_name):
        generator = None
        if field_name not in self.__generators:
            generator = RelatedDataGenerator(self)
            self.__generators[field_name] = generator
        
        generator.set_field_name(field_name)
        return generator

    def get_choice(self):
        return self.__choice

    def set_choice(self, choice):
        self.__choice = choice

    def reset_choice(self):
        self.__choice = None

class RelatedDataGenerator(ValueGenerator):
    field_index = -1
    def __init__(self, related_data_source):
        self.related_data_source = related_data_source

    def set_field_name(self, field_name):
        self.field_index = self.related_data_source.get_index(field_name)
        # print("index:", self.field_index)

    def __next__(self):
        choice = self.related_data_source.get_choice()
        if choice is None:
            choice = random.choice(self.related_data_source.get_lines())
            self.related_data_source.set_choice(choice)
        
        value = choice[self.field_index]
        # print("V", line, self.field_index, value)
        return value

class DatetimeRange(ValueGenerator):
    def initialize(self):
        if 'begin' in self.flags:
            self.begin = unixtime(self.flags['begin'])
        if 'end' in self.flags:
            self.end = unixtime(self.flags['end'])

    def __next__(self):
        self.values = range(self.begin, self.end)
        ts = random.choice(self.values)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) 

class IntegerRange(ValueGenerator):
    values = None
    current = None
    step = 1
    def adapt(self, values):
        self.values = values

    def initialize(self):
        if 'begin' in self.flags:
            self.current = self.flags['begin']
        if 'step' in self.flags:
            self.step = self.flags['step']

    def __next__(self):
        if self.values is None:
            self.values = range(self.flags['begin'], self.flags['end'])
        if 'order' in self.flags:
            if self.flags['order'] == 'asc':
                self.current += self.step
                return self.current
            elif self.flags['order'] == 'desc':
                self.current -= self.step
                return self.current

        return random.choice(self.values)        

"""
"""
class EnglishName(ValueGenerator):
    names = None
    def initialize(self):
        self.names = self.load('english_names.txt')

    def load(self, filename):
        # TODO: load names from a file
        return ['Albert', 'Bob', 'Helen', 'McDonald', 'Mike', 'Lucy', 'Lily', 'Sophy', 'Chris', 'John']

    def __next__(self):
        if self.names is None:
            self.initialize()
        try:
            name = random.choice(self.names)
            if self.flags['unique']:
                self.names.remove(name)
            return name            
        except:
            # Resource not enough for unique random
            return "<None>"


"""
"""
class ChineseName(ValueGenerator):
    names = None

    def initialize(self):
        self.names = self.__load('chinese_names.txt')

    def __load(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), file.readlines())))

    def __next__(self):
        if self.names is None:
            self.initialize()
        try:
            name = random.choice(self.names)
            if self.unique:
                self.names.remove(name)
            return name            
        except:
            # Resource not enough for unique random
            return "<None>"


class ChinaMobile(ValueGenerator):
    cache = set()

    def __next__(self):
        t = str(random.choice([3, 4, 5])) + str(random.randint(0, 9))
        return "1%s%s%s" % (t, random.randint(1000, 9999), random.randint(1000, 9999))

    def __iter__(self):
        count = 0
        while True:
            if count > 10:
                break
            count += 1
            v = next(self)
            yield v

"""
main class for insertion
"""
class Insert:
    table_name = None
    options = None
    related_data_source = None
    format = 'insert'

    def __init__(self, table_name, **options):
        self.table_name = table_name
        self.options = options
        self.fields_order = None

    def set_related_data_source(self, related_data_source):
        self.related_data_source = related_data_source

    def __generate_insert(self, times, i):
        f, v = [], []
        for field in self.fields_order:
            f.append(field)
            generator = self.generators[field]
            if generator is None:
                v.append("null")
            else:
                v.append("'%s'" % str(next(generator)))
        if self.format == 'inserts':
            return "insert into `%s` (%s) values (%s);" % (self.table_name, ", ".join(f), ", ".join(v))
        elif self.format == 'insert':
            return "(%s)%s " % (", ".join(v), ',' if times - i > 1 else ';')
        elif self.format == 'csv':
            v = list(map(lambda x: x.strip("'"), v))
            return ','.join(v)

    def generate(self, times, file):
        self.generators = {}

        for g in self.options:
            self.generators[g] = self.get_generator(g)
        # set fields order
        if self.fields_order is None:
            self.fields_order = []
            for g in self.options:
                self.fields_order.append(g)

        if self.format == 'csv':
            file.write(','.join(self.fields_order) + "\n")
        elif self.format == 'insert':
            insert = "insert into `%s` (%s) values " % (self.table_name, ", ".join(self.fields_order))
            file.write(insert + "\n")

        for i in range(0, times):
            yield self.__generate_insert(times, i)

            if self.related_data_source is not None:
                self.related_data_source.reset_choice()

    def set_fields_order(self, fields_order):
        self.fields_order = fields_order

    def perform(self, times, filename, format='inserts'):
        encoding = 'utf-8'
        if format == 'csv':
            encoding = 'gbk'
        file = open(filename, 'w', encoding=encoding)

        self.format = format
        for line in self.generate(times, file):
            file.write(line + "\n")

        file.close()

    def get_generator(self, g):
        config = self.options[g]
        if isinstance(config, ValueGenerator):
            return config
        elif isinstance(config, list):
            r = ListGenerator()
            r.adapt(config)
            return r
        elif isinstance(config, range):
            r =  IntegerRange()
            r.adapt(config)
            return r
        return None



"""
"""
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(1)
        exit()

    i = Insert('kx_user', 
        user_id=None,
        company_id=[2, 3, 5], 
        username=ChineseName(unique=True), 
        age=range(20, 90), 
        mobile=ChinaMobile(),
        time=DatetimeRange(begin='2015-12-23', end='2016-12-23'),
        order_id=IntegerRange(begin=100, end=1000, step=2, order='asc'))

    i.set_fields_order(['user_id', 'username', 'age', 'mobile', 'company_id', 'time', 'order_id'])
    i.perform(20)
















