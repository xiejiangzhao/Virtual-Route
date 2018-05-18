import json
from typing import List


def interface_int_to_str(interface: int) -> str:
    if interface == 0:
        return "On-Link"
    s4 = interface % 256
    interface //= 256
    s3 = interface % 256
    interface //= 256
    s2 = interface % 256
    interface //= 256
    s1 = interface % 256
    return f"{s1}.{s2}.{s3}.{s4}"


class RouteTable:
    Table = []

    def __init__(self, json_file: str = ''):
        """
        Init Route Table,will init Table by json file
        :param json_file: json file name
        """
        if json_file == '':
            self.Table = []
        else:
            with open(json_file, 'r') as file:
                self.Table = json.load(file)

    def print_table(self) -> None:
        """
        print whole route table
        :return: without return
        """
        print('Dst_ip          Dst_port Next_ip         Next_port Interface')
        for i in self.Table:
            print(f"{i['dst_ip']:<15} {i['dst_port']:<5}    {i['next_ip']:<15} {i['next_port']:<5}     "
                  f"{interface_int_to_str(i['interface']):<15}")

    def find_next(self, dst_ip: str, dst_port: int) -> List:
        """
        find the next jump
        :param dst_ip: destination ip
        :param dst_port: destination port
        :return: a list with two team,next_ip and next_port
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                return [row['next_ip'], row['next_port']]
        return []

    def is_on_link(self, dst_ip: str, dst_port: int) -> bool:
        """
        :param dst_ip: destination ip
        :param dst_port: destination port
        :return: return True if on-link
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                return row['interface'] == 0

    def update_table(self, dst_ip: str, dst_port: int, next_ip: str, next_port: int, interface: int = '') -> bool:

        """
        update table,if table don't have it,create;esle modify it
        :param dst_ip: destination ip
        :param dst_port: destination port
        :param next_ip: next ip
        :param next_port: next port
        :param interface: interface info
        :return: return if changed
        """
        changed = False
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                changed = row['next_ip'] != next_ip or row['next_port'] != next_port
                row['next_ip'] = next_ip
                row['next_port'] = next_port
                if interface != '':
                    row['interface'] = interface
                return changed
        self.Table.append({"dst_ip": dst_ip, "dst_port": dst_port, "next_ip": next_ip, "next_port": next_port,
                           "interface": 1})
        return True

    def update_table_by_table(self, route_table: list) -> bool:
        changed = False
        for row in route_table:
            res = self.update_table(row['dst_ip'], row['dst_port'], row['next_ip'], row['next_port'], row['interface'])
            changed = changed or res
        return changed

    def delete_team(self, dst_ip: str, dst_port: int) -> bool:
        """
        :param dst_ip:
        :param dst_port:
        :return: if delete success,return true;else false
        """
        for row in self.Table:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                self.Table.remove(row)
                return True
        return False

    def get_neibour(self) -> List:
        """
        :return:嵌套列表,里面每一个列表包含两个元素,ip和port
        """
        res = []
        for row in self.Table:
            if row['interface'] == 0:
                res.append([row['dst_ip'], row['dst_port']])
        return res

    def get_all_member(self) -> List:
        res = []
        for row in self.Table:
            res.append([row['dst_ip'], row['dst_port']])
        return res

    def save_table(self, json_file) -> None:
        with open(json_file, 'w') as file:
            json.dump(self.Table, file)


if __name__ == '__main__':
    test = [{"dst_ip": "127.0.0.1", "dst_port": 8001, "next_ip": "127.0.0.1", "next_port": 8002, 'interface': 0}]
    with open('test.json', 'w') as f:
        json.dump(test, f)
    a = RouteTable('test.json')
    a.print_table()
    b = a.is_on_link('127.0.0.1', 8001)
    c = a.find_next('127.0.0.1', 8001)
    a.update_table('192.168.0.1', 8034, '127.0.0.1', 4001, 1)
    a.update_table('255.255.255.255', 65535, '255.255.255.254', 65534, 4294967295)
    a.print_table()
