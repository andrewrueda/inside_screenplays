"""Build graph of a screenplay's character structure given parsed information from read_script.py"""

from pdf_to_txt import *
from ScreenPy.screenpile import *
from read_script import *

import os
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network
import community as community_louvain
import h5py


def build_graph(char_list, polarities, adjacency_matrix, scale_factor=.995):
    """Computes graph attributes and produces .html visualization."""
    G = nx.from_numpy_array(adjacency_matrix)
    mapping = {i: char_list[i] for i in range(len(char_list))}
    G = nx.relabel_nodes(G, mapping)

    # degrees = dict(G.degree())
    degrees = dict(G.degree(weight='weight'))
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos=pos, with_labels=True)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5)

    for u, v, data in G.edges(data=True):
        data['value'] = data['weight']

    nx.set_node_attributes(G, degrees, 'size')

    # Degree centrality
    degrees = dict(sorted(degrees.items(), key=lambda item: item[1], reverse=True))
    degree_centrality = {char: indx+1 for indx, char in enumerate(degrees.keys())}
    nx.set_node_attributes(G, degree_centrality, 'Degree Centrality rank')

    # Betweenness centrality
    betweenness_dict = dict(sorted(nx.betweenness_centrality(G).items(), key=lambda item: item[1], reverse=True))
    betweenness_centrality = {char: indx+1 for indx, char in enumerate(betweenness_dict.keys())}
    nx.set_node_attributes(G, betweenness_centrality, 'Betweenness Centrality rank')

    # Closeness centrality
    closeness_dict = dict(sorted(nx.closeness_centrality(G).items(), key=lambda item: item[1], reverse=True))
    closeness_centrality = {char: indx+1 for indx, char in enumerate(closeness_dict.keys())}
    nx.set_node_attributes(G, closeness_centrality, 'Closeness Centrality rank')

    # Community Detection
    communities = community_louvain.best_partition(G)

    # Set Polarity
    polarities = {char: f"{polarity:.3f}" for char, polarity in zip(char_list, polarities)}
    nx.set_node_attributes(G, polarities, 'Dialogue Sentiment')

    for node, attributes in G.nodes(data=True):
        info = f"Name: {node}\n"
        for att, value in attributes.items():
            info += f"{att}: {value}\n"

        G.nodes[node]['title'] = info

    nx.set_node_attributes(G, communities, 'group')
    net = Network(notebook=True, width="1000px", height="700px", bgcolor="#222222", font_color="white")
    net.repulsion()
    net.from_nx(G)

    # Scale sizes
    if degrees:
        quantile = np.quantile([weight for char, weight in degrees.items()], scale_factor)
    else:
        quantile = 0
    scaled_sizes = {char: np.minimum(size, quantile) for char, size in degrees.items()}
    for node in net.nodes:
        size = scaled_sizes[node['id']]
        node['size'] = size
    # net.show("test_html/output.html") # output to test .html
    return net


def compile_catalog(txt_dir="ScreenPy/imsdb_raw_nov_2015",
                    destination_dir="movie_catalog.h5", append_mode=False):
    file_mode = 'a' if append_mode else 'w'
    with h5py.File('movie_catalog.h5', file_mode) as f:
        titles = set(f.keys()) if append_mode else set()
        new_entries = 0
        for root, dirs, files in os.walk(txt_dir):
            for file in files:
                if file.endswith("txt"):
                    name = "_".join(file.split(".")[:-1])
                    if name not in titles:
                        titles.add(name)
                        script = txt_to_text_buffer(os.path.join(root, file))
                        parsed_script = annotate(script)
                        char_list, polarities, adjacency_matrix = read_script(parsed_script)
                        if char_list:
                            grp = f.create_group(name)
                            grp.create_dataset('chars', data=char_list, dtype=h5py.string_dtype(encoding="utf-8"))
                            grp.create_dataset('polarities', data=np.array(polarities))
                            grp.create_dataset('adjacency_matrix', data=adjacency_matrix)
                            print(f"Added: {name}")
                            new_entries += 1
    print(f"\nAdded {new_entries} Entries")


def add_movie(name, char_list, polarities, adjacency_matrix, catalog_file="movie_catalog.h5"):
    with h5py.File(catalog_file, 'a') as f:
        titles = set(f.keys())
        if name not in titles:
            grp = f.create_group(name)
            grp.create_dataset('chars', data=char_list, dtype=h5py.string_dtype(encoding="utf-8"))
            grp.create_dataset('polarities', data=np.array(polarities))
            grp.create_dataset('adjacency_matrix', data=adjacency_matrix)
            return f"{name} Added!"
        else:
            grp = f[name]
            del grp['chars']
            del grp['polarities']
            del grp['adjacency_matrix']
            grp.create_dataset('chars', data=char_list, dtype=h5py.string_dtype(encoding="utf-8"))
            grp.create_dataset('polarities', data=np.array(polarities))
            grp.create_dataset('adjacency_matrix', data=adjacency_matrix)
            return f"{name} Updated!"


def delete_movie(name, catalog_file="movie_catalog.h5"):
    with h5py.File(catalog_file, 'a') as f:
        del f[name]


def get_movie(name, catalog_file="movie_catalog.h5"):
    with h5py.File(catalog_file, 'r') as f:
        char_list = [char.decode('utf-8') for char in f[name]['chars'][:]]
        polarities = f[name]['polarities'][:]
        adjacency_matrix = f[name]['adjacency_matrix'][:]
        return char_list, polarities, adjacency_matrix


if __name__ == "__main__":
    movie = "harrypotterandthehalfbloodprince"
    pdf_to_txt(f"test_files/test_pdf/{movie}.pdf")
    annotate_disk(f"test_files/test_txt/{movie}.txt")
    char_list, adjacency_matrix = read_script(f"test_files/test_json/{movie}.json", from_disk=True, do_print=False)
    build_graph(char_list, adjacency_matrix)

    # movie = 'starwarstheempirestrikesback'
    # annotate_disk(f"ScreenPy/imsdb_raw_nov_2015/Sci-Fi/{movie}.txt")
    # char_list, adjacency_matrix = read_script(f"test_json/{movie}.json", from_disk=True)
    # add_movie(movie, char_list, adjacency_matrix)
    # build_graph(char_list, adjacency_matrix)

    # char_list, adjacency_matrix = get_movie("magnolia")
    # char_list, polarities, adjacency_matrix = read_script("ScreenPy/ParserOutput/Drama/twinpeaks.json", from_disk=True)
    # build_graph(char_list, polarities, adjacency_matrix)

    # compile_catalog()
    # compile_catalog(txt_dir="test_txt", append_mode=True)
