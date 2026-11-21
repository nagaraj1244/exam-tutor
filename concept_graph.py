import networkx as nx

def create_concept_graph():
    graph = nx.DiGraph()

    concepts = [
        "Electric Current",
        "Voltage",
        "Resistance",
        "Ohm's Law",
        "Series Circuits",
        "Parallel Circuits",
        "Electric Power"
    ]

    graph.add_nodes_from(concepts)

    graph.add_edges_from([
        ("Electric Current", "Ohm's Law"),
        ("Voltage", "Ohm's Law"),
        ("Resistance", "Ohm's Law"),
        ("Ohm's Law", "Series Circuits"),
        ("Ohm's Law", "Parallel Circuits"),
        ("Voltage", "Electric Power"),
        ("Electric Current", "Electric Power")
    ])

    return graph