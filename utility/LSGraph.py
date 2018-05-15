import json
from utility.RouteTable import RouteTable


class LSGraph:
    Graph = []
    Routetable: RouteTable = None
    Node_mapping: [list] = [{'ip': '127.0.0.1', 'port': 8001, 'interface': 8002}]

    def __init__(self, json_file: str = '', Node_mapping_file='', routetable: RouteTable = ''):
        self.Routetable = routetable
        if json_file == '':
            self.Graph = []
        else:
            with open(json_file, 'r') as f:
                self.Graph = json.load(f)
        if Node_mapping_file == '':
            self.Node_mapping = []
        else:
            with open(Node_mapping_file, 'r') as f:
                self.Node_mapping = json.load(f)

    def save_table(self, json_file) -> None:
        with open(json_file, 'w') as f:
            json.dump(self.Graph, f)

    def get_graph_index(self, ip: str, port: int) -> int:
        for i in range(len(self.Node_mapping)):
            if self.Node_mapping[i]['ip'] == ip and self.Node_mapping[i]['port'] == port:
                return i

    def update_route_table(self, ip: str, port: int) -> None:
        path = self.dijkstra(self.Graph, self.get_graph_index(ip, port))
        for i in range(len(path)):
            dst_ip = self.Node_mapping[i]['ip']
            dst_port = self.Node_mapping[i]['port']
            interface = self.Node_mapping[i]['interface']
            if len(path[i]) != 0:
                next_index = path[i][0]
            else:
                next_index = self.get_graph_index(ip, port)
            next_ip = self.Node_mapping[next_index]['ip']
            next_port = self.Node_mapping[next_index]['port']
            self.Routetable.update_table(dst_ip, dst_port, next_ip, next_port, interface)
        pass

    def dijkstra(self, graph, src):
        # 判断图是否为空，如果为空直接退出
        if graph is None:
            return None
        nodes = [i for i in range(len(graph))]  # 获取图中所有节点
        visited = []  # 表示已经路由到最短路径的节点集合
        if src in nodes:
            visited.append(src)
            nodes.remove(src)
        else:
            return None
        distance = {src: 0}  # 记录源节点到各个节点的距离
        for i in nodes:
            distance[i] = graph[src][i]  # 初始化
        # print(distance)
        path = {src: {src: []}}  # 记录源节点到每个节点的路径
        k = pre = src
        while nodes:
            mid_distance = float('inf')
            for v in visited:
                for d in nodes:
                    new_distance = graph[src][v] + graph[v][d]
                    if new_distance < mid_distance:
                        mid_distance = new_distance
                        graph[src][d] = new_distance  # 进行距离更新
                        k = d
                        pre = v
            distance[k] = mid_distance  # 最短路径
            path[src][k] = [i for i in path[src][pre]]
            path[src][k].append(k)
            # 更新两个节点集合
            visited.append(k)
            nodes.remove(k)
        return path[0]


if __name__ == '__main__':
    Node_mapping: list = [{'ip': '127.0.0.1', 'port': 8001, 'interface': 8002}]
    with open('node_map.json', 'w') as f:
        json.dump(Node_mapping, f)
    graph_list = [[0, 2, 7], [2, 0, 1], [7, 1, 0]]
    with open('LStest.json', 'w') as f:
        json.dump(graph_list, f)
    a = LSGraph('LStest.json', 'node_map.json')
    a.update_route_table('127.0.0.1', 8001)
