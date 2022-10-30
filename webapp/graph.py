from pyvis.network import Network
from typing import List
from PIL.ImageColor import getcolor
from functools import reduce
from utilities.colors import *
from log import Logger

import networkx as nx
import pandas as pd

UNK_ = '기타'
ENTIRE_NODE_SIZE = 15
NEI_NODE_SIZE = 20
KEY_NODE_SIZE = 25

KEY_BORDER_SIZE = 4

ENTIRE_NODE_COLOR = "#92E5B1"
ENTIRE_BORDER_COLOR = "#8FCDA6"
ENTIRE_HOVER_COLOR= "#8FCDA6"

NEI_NODE_COLOR = "#C2ED9E"
NEI_BORDER_COLOR = "#A9E17A"
NEI_HOVER_COLOR= "#A9E17A"

KEY_NODE_COLOR = "#FF8787"
KEY_BORDER_COLOR = "#F96969"
KEY_HOVER_COLOR= "#F96969"


ENTIRE_EDGE_WIDTH = 5
KEY_EDGE_WIDTH = 15

ENTIRE_EDGE_COLOR = "#B8B8B8"
KEY_EDGE_COLOR = "#F8C4B4"


ENTIRE_LABEL = { 'color': "#797979", 'size': 10, 'face': "arial", 
  'background': "none", 'strokeWidth': 0, 'strokeColor': "#ffffff", 'align': "center" }

NEIGHBOR_LABEL = { 'color': "#383838", 'size': 13, 'face': "arial", 
  'background': "none", 'strokeWidth': 0, 'strokeColor': "#ffffff", 'align': "center" }

KEY_LABEL = { 'color': "#383838", 'size': 20, 'face': "arial", 
  'background': "none", 'strokeWidth': 0.7, 'strokeColor': "#383838", 'align': "center" }


def load_data(filepath : str, logger : Logger):
    def _isnan(string):
        return string != string

    def _read_csv(filepath):
        from pandas.io.parsers import ParserError
        try:
            df = pd.read_csv(filepath, converters={
                'id': int
            })
        except ParserError as e:
            logger.warning("Convert seperator (comma -> tap)")
            df = pd.read_csv(filepath, sep= '\t', converters={
                'id': int
            })
        return df

    data = _read_csv(filepath)
    data['category'] = [int(category) if not _isnan(category) else -1 for category in data.category]
    data['neighbors'] = [neighbors_str.split() if not _isnan(neighbors_str) else [] for neighbors_str in data.edge]
    data['neighbors'] = [list(map(int, neighbors)) for neighbors in data.neighbors]

    return data
  
def find_nodeid(data : pd.DataFrame, tgt_word : str, logger : Logger):
    try:
        node_id = int(data[data.word == tgt_word.strip()].id.values[0])
    except IndexError:
        logger.error("Unknown Keyword %s" % tgt_word)
        node_id = -1
    return node_id
  
def find_nodename(data : pd.DataFrame, tgt_id : int, logger : Logger):
    try:
        node_name = str(data[data.id == tgt_id].word.values[0])
    except IndexError:
        logger.error("Unknown Word ID %d" % tgt_id)
        node_name = UNK_
    return node_name
  
  
def build_graph(data : pd.DataFrame, logger : Logger):
    nx_graph = nx.Graph()

    for row in data.iterrows():
        d = row[1]
        cur_node = d.id
        neighbor_nodes = d.neighbors

        if len(neighbor_nodes) == 0:
            logger.warning("Nothing connected with %s " % d.word)

        nx_graph.add_node(cur_node, size=ENTIRE_NODE_SIZE, label=d.word)
        list(map(lambda neighbor_node: nx_graph.add_edge(cur_node, neighbor_node), neighbor_nodes))

    return nx_graph
  
def configure_graph_option(graph : nx.Graph, node_conf : dict, edge_conf : dict):
    _ = list(map(lambda n: graph.nodes[n].update(node_conf), graph.nodes))
    _ = list(map(lambda e: graph.edges[e].update(edge_conf), graph.edges))
    return graph

def configure_group(graph : nx.Graph, node_list, node_conf : dict):
    _ = list(map(lambda n: graph.nodes[n].update(node_conf), node_list))
    return graph

  
def highlighting_keywords(graph : nx.Graph, keywords : List[str], data : pd.DataFrame, alpha : int or str, logger : Logger, color_adjust=50):
    if isinstance(alpha, int):
        alpha = int_to_hex_str(alpha)

    key_ids = [find_nodeid(data, key, logger=logger) for key in keywords]
    
    while -1 in key_ids:
        logger.warning("Pass highlighting unknown keywords : %s " % (keywords[key_ids.index(-1)]))
        key_ids.pop(key_ids.index(-1))

    neighbors = [list(graph.neighbors(id)) for id in key_ids]
    neighbors = reduce(lambda x, y : x + y, neighbors)
    
    key_edges = [list(graph.edges(id)) for id in key_ids]
    key_edges = reduce(lambda x, y : x + y, key_edges)

    def _adjust_color(prev_rgb : tuple, color_adjust=color_adjust, alpha=alpha):
        adj_rgb = prev_rgb
        adj_html_cd =rgb_to_hex(*adj_rgb)
        return "%s%s" % (adj_html_cd, alpha)
    
    def _update_node(graph, cur_node, node_type='basic', **kwargs):
        if node_type == 'basic':
            graph.nodes[cur_node].update({'color' : {'border' : ENTIRE_BORDER_COLOR, 
                                                    'background' : ENTIRE_NODE_COLOR,
                                                    'highlight': {'border' : ENTIRE_BORDER_COLOR, 'background' : ENTIRE_HOVER_COLOR },
                                                    'hover' : {'border' : ENTIRE_BORDER_COLOR, 'background' : ENTIRE_HOVER_COLOR }}, 
                                            'size' : ENTIRE_NODE_SIZE, 'font' : ENTIRE_LABEL})
        elif node_type == 'key':
            graph.nodes[cur_node].update({'size' : KEY_NODE_SIZE, 
                                            'color' : {'border' : KEY_BORDER_COLOR, 
                                                       'background' : KEY_NODE_COLOR,
                                                       'highlight': {'border' : KEY_BORDER_COLOR, 'background' : KEY_HOVER_COLOR },
                                                       'hover' : {'border' : KEY_BORDER_COLOR, 'background' : KEY_HOVER_COLOR }},
                                            'borderWidth': kwargs['borderwidth'],
                                            'font' : KEY_LABEL,
                                            'labelHighlightBold' : 0})
        else:
            graph.nodes[cur_node].update({'size' : NEI_NODE_SIZE, 
                                            'color' : {'border' : NEI_BORDER_COLOR, 
                                                       'background' : NEI_NODE_COLOR,
                                                       'highlight': {'border' : NEI_BORDER_COLOR, 'background' : NEI_HOVER_COLOR },
                                                       'hover' : {'border' : NEI_BORDER_COLOR, 'background' : KEY_HOVER_COLOR }},
                                            'font' : NEIGHBOR_LABEL,
                                            'labelHighlightBold' : 0})
        return
    
    def _update_edge(graph, cur_edge, edge_type='basic', **kwargs):
        if edge_type == 'basic':
            graph.edges[cur_edge].update({'color' : ENTIRE_EDGE_COLOR, 'width' : ENTIRE_EDGE_WIDTH})
        else:
            graph.edges[cur_edge].update({'width' : kwargs['edge_width'], 'color' : kwargs['edge_color']})
        return
    
    _ = list(map(lambda n: _update_node(graph, n), [n for n in graph.nodes if not n in neighbors + key_ids]))
    _ = list(map(lambda e: _update_edge(graph, e), [e for e in graph.edges if not e in key_edges]))

    _ = list(map(lambda e: _update_edge(graph, e, edge_type='key', edge_width=KEY_EDGE_WIDTH, edge_color=KEY_EDGE_COLOR), key_edges))
    _ = list(map(lambda n: _update_node(graph, n, node_type='neighbor', node_size=NEI_NODE_SIZE), neighbors))
    _ = list(map(lambda n: _update_node(graph, n, node_type='key', node_size=KEY_NODE_SIZE, borderwidth=KEY_BORDER_SIZE, bordercolor=KEY_BORDER_COLOR), key_ids))
    
    return graph

def build_highlighted_graph(data : pd.DataFrame, keywords : List[str], logger : Logger):
    graph = build_graph(data, logger=logger)
    groups = list(set(data.category.tolist()))

    group_colors = get_colors(len(groups), colors)
    configure_graph_option(graph, node_conf={'size':ENTIRE_NODE_SIZE}, edge_conf={'width':ENTIRE_EDGE_WIDTH, 'color': ENTIRE_EDGE_COLOR})
    for g, c in zip(groups, group_colors):
        labels = data[data.category == g].word.tolist()
        node_ids = [find_nodeid(data, label, logger=logger) for label in labels]
        configure_group(graph, node_list = node_ids,
                            node_conf={'color': c})
        
    h_graph = highlighting_keywords(graph, keywords, data, alpha='AA', logger=logger, color_adjust=50)
    
    nt = Network()
    nt.from_nx(h_graph)
    return nt.nodes, nt.edges