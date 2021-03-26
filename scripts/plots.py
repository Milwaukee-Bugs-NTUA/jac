#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

def plot_results(data,file, title):
    x = np.arange(5)
    width = 0.35 
    labels = ["k = 1","k = 3, ch.","k = 3, ev.","k = 5, ch.","k = 5, ev."]

    # Figure
    fig, ax = plt.subplots()
    ax.bar(labels, data, width)
    ax.set_ylabel('Throughput')
    ax.set_xlabel('Experiements')
    ax.set_title(title)
    fig.tight_layout()
    # Save figure
    plt.savefig(file,dpi=300)


if __name__ == "__main__":

    with open("../test_data/insert_times.txt", "rt") as f:
        data = []
        f.readline()
        for i in range(5):
            t = int(f.readline())/500
            data.append(t)
    print("Saving 'Insert' experiment figure.")           
    plot_results(data,"../test_data/insert.png","Insert Experiment")
    with open("../test_data/query_times.txt", "rt") as f:
        data = []
        f.readline()
        for i in range(5):
            t = int(f.readline())/500
            data.append(t)         
    print("Saving 'Query' experiment figure.")             
    plot_results(data,"../test_data/query.png","Query Experiment")
