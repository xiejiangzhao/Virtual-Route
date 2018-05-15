import json


class Route_Table:
    Table = []

    def __init__(self, json_file=''):
        """
        Init Route Table,will init Table by json file
        :param json_file: json file name
        """
        if json_file == '':
            self.Table = []
        else:
            with open(json_file, 'r') as f:
                self.Table = json.load(f)

    def print_table(self):
        """
        print whole route table
        :return: without return
        """
        print('Dst_ip Dst_port Next_ip Next_port interface')
        for row in self.Table:
            print(row['dst_ip'] + ' ' + str(row['dst_port']) + ' ' + row['next_ip'] + ' ' + str(
                row['next_port']) + ' ' + str(row['interface']))

    def find_next(self, dst_ip, dst_port):
        """
        find the next jump
        :param dst_ip: destination ip
        :param dst_port: destination port
        :return: a list with two team,next_ip and next_port
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                return [row['next_ip'], row['next_port']]
        return None

    def is_onlink(self, dst_ip, dst_port):
        """
        :param dst_ip: destination ip
        :param dst_port: destination port
        :return: return interface value
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                return row['interface']

    def update_table(self, dst_ip, dst_port, next_ip, next_port, interface):
        """
        update table,if table don't have it,create;esle modify it
        :param dst_ip: destination ip
        :param dst_port: destination port
        :param next_ip: next ip
        :param next_port: next port
        :param interface: interface info
        :return: without return
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                row['next_ip'] = next_ip
                row['next_port'] = next_port
                row['interface'] = interface
                return
        self.Table.append({"dst_ip": dst_ip, "dst_port": dst_port, "next_ip": next_ip, "next_port": next_port,
                            'interface': interface})
        return


if __name__ == '__main__':
    test = [{"dst_ip": "127.0.0.1", "dst_port": 8001, "next_ip": "127.0.0.1", "next_port": 8002, 'interface': 0}]
    with open('test.json', 'w') as f:
        json.dump(test, f)
    a = Route_Table('test.json')
    a.print_table()
    b=a.is_onlink('127.0.0.1',8001)
    c=a.find_next('127.0.0.1',8001)
    d=a.update_table('192.168.0.1',8034,'127.0.0.1',4001,1)
    a.print_table()
