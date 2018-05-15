from utility.RouteTable import RouteTable
from utility.DVTable import DVTable
from utility.LSGraph import LSGraph
import json

if __name__ == '__main__':
    Aroute = RouteTable('config/Aroute.json')
    Broute = RouteTable('config/Broute.json')
    Croute = RouteTable('config/Croute.json')
    Droute = RouteTable('config/Droute.json')
    Eroute = RouteTable('config/Eroute.json')
    Froute = RouteTable('config/Froute.json')
    ADV = DVTable('config/ADV.json', Aroute,'127.0.0.1',9000)
    BDV = DVTable('config/BDV.json', Broute,'127.0.0.1',9001)
    CDV = DVTable('config/CDV.json', Croute,'127.0.0.1',9002)
    DDV = DVTable('config/DDV.json', Droute,'127.0.0.1',9003)
    EDV = DVTable('config/EDV.json', Eroute,'127.0.0.1',9004)
    FDV = DVTable('config/FDV.json', Froute,'127.0.0.1',9005)
    BDV.update_table_by_table('127.0.0.1', 9000, ADV.DVTable)
    ADV.update_table_by_table('127.0.0.1', 9001, BDV.DVTable)
    CDV.update_table_by_table('127.0.0.1', 9001, BDV.DVTable)
    DDV.update_table_by_table('127.0.0.1', 9001, BDV.DVTable)
    AGraph=LSGraph('config/LSGraph.json','config/Mapping.json',Aroute)
    AGraph.update_route_table('127.0.0.1',9000)
    BGraph = LSGraph('config/LSGraph.json', 'config/Mapping.json', Broute)
    BGraph.update_route_table('127.0.0.1', 9001)
    print("")
