from utility.RouteTable import RouteTable
import json
import sys


class DVTable:
    DVTable = []
    own_ip = ''
    own_port = 0
    Routetable: RouteTable = None

    def __init__(self, json_file: str = '', routetable: RouteTable = '', own_ip: str = '', own_port: int = 0):
        self.own_ip = own_ip
        self.own_port = own_port
        if json_file == '':
            self.DVTable = []
        else:
            with open(json_file, 'r') as f:
                self.DVTable = json.load(f)
        self.Routetable = routetable

    def print_table(self) -> None:
        """
        print whole route table
        :return: without return
        """
        print('Dst_ip          Dst_port Next_ip         Next_port Cost')
        for i in self.DVTable:
            print(f"{i['dst_ip']:<15} {i['dst_port']:<5}    {i['next_ip']:<15} {i['next_port']:<5}     "
                  f"{i['cost']:<5}")

    def get_cost(self, dst_ip: str, dst_port: int) -> int:
        for row in self.DVTable:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                return row['cost']

    def update_table(self, src_ip: str, src_port: int, dst_ip: str, dst_port: int,
                     cost: int) -> bool:
        """
        :param table_ip: the ip of the who boardcast the table
        :param table_port: same as above
        :param dst_ip:
        :param dst_port:
        :param next_ip:
        :param next_port:
        :param cost:
        :return: if table is change,return true
        """
        cost_to_table = self.get_cost(src_ip, src_port)
        for row in self.DVTable:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                if row['cost'] > cost + cost_to_table:
                    row['next_ip'] = src_ip
                    row['next_port'] = src_port
                    row['cost'] = cost + cost_to_table
                    self.Routetable.update_table(dst_ip, dst_port, src_ip, src_port)
                    return True
                else:
                    return False
        if dst_ip != self.own_ip or dst_port != self.own_port:
            self.DVTable.append(
                {"dst_ip": dst_ip, "dst_port": dst_port, "next_ip": src_ip, "next_port": src_port,
                 'cost': cost + cost_to_table})
            self.Routetable.update_table(dst_ip, dst_port, src_ip, src_port)
            return True
        else:
            return False

    def route_offline(self, src_ip: str, src_port: int) -> None:
        for row in self.DVTable:
            if row['next_ip'] == src_ip and row['next_port'] == src_port:
                row['cost'] = float(sys.maxsize)

    def update_table_by_table(self, src_ip: str, src_port: int, route_table: list) -> None:
        change = False
        for row in route_table:
            res = self.update_table(src_ip, src_port, row['dst_ip'], row['dst_port'],
                                    row['cost'])
            change = change or res
        return change

    def delete_team(self, dst_ip: str, dst_port: int) -> bool:
        """
        :param dst_ip:
        :param dst_port:
        :return: if delete success,return true;else false
        """
        for row in self.DVTable:
            if row['dst_ip'] == dst_ip and row['dst_port'] == dst_port:
                self.DVTable.remove(row)
                return True
        return False

    def save_table(self, json_file) -> None:
        with open(json_file, 'w') as f:
            json.dump(self.DVTable, f)


if __name__ == '__main__':
    a = RouteTable('test.json')
