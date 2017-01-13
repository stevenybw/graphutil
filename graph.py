import copy
""" Graph For Python"""


class Edge:
    def __init__(self, src, dst, src_output, dst_input, tensor_shape, dtype):
        self.src = src
        self.dst = dst
        self.src_output = src_output
        self.dst_input = dst_input
        self.tensor_shape = tensor_shape
        self.dtype = dtype


class Graph:
    def __init__(self):
        self._V = set()

        self._edges = list()
        self._edges_from_node_id = dict()
        self._edges_to_node_id = dict()
        
        self._attribute = dict()

    def transpose(self) -> 'Graph':
        transposed_g = Graph()
        for e in self._edges:
            transposed_g.connect(e.src, e.dst, src_output_index=e.src_output, dst_input_index=e.dst_input)
        return transposed_g

    def sub_graph(self, vertexes) -> 'Graph':
        """ Create a sub-graph with specified vertices

        :param vertexes: The vertexes of the sub graph
        :return:
        """
        sub_graph = Graph()
        sub_vertex = set(vertexes)
        for v in sub_vertex:
            if v not in self._V:
                raise RuntimeError("vertex " + str(v) + " does not exist in the graph")
            else:
                sub_graph.possibly_add_node(v)
        for e in self._edges:
            if e.src in sub_vertex and e.dst in sub_vertex:
                sub_graph.connect(e.src, e.dst, src_output_index=e.src_output, dst_input_index=e.dst_input)
        return sub_graph

    def nodes(self) -> set:
        return set(self._V)

    def in_nodes(self, node_id: int) -> list:
        return [e.src for e in self._edges_to_node_id[node_id]]

    def out_nodes(self, node_id: int) -> list:
        return [e.dst for e in self._edges_from_node_id[node_id]]

    def in_edges(self, node_id: int) -> list:
        return list(self._edges_to_node_id[node_id])

    def out_edges(self, node_id: int) -> list:
        return list(self._edges_from_node_id[node_id])

    def num_nodes(self):
        return len(self._V)

    def possibly_add_node(self, u):
        if u not in self._V:
            self._V.add(u)
            self._edges_from_node_id[u] = list()
            self._edges_to_node_id[u] = list()
            val = dict()
            val['in_degree'] = 0
            val['out_degree'] = 0
            self._attribute[u] = val

    def connect(self, src, dst, src_output_index=0, dst_input_index=0, tensor_shape=None, dtype=None):
        self.possibly_add_node(src)
        self.possibly_add_node(dst)
        edge = Edge(src, dst, src_output_index, dst_input_index, tensor_shape, dtype)
        self._edges_from_node_id[src].append(edge)
        self._edges_to_node_id[dst].append(edge)
        self._edges.append(edge)

    def set_attribute(self, node_id, name, value):
        self.possibly_add_node(node_id)
        self._attribute[node_id][name] = value

    def attribute(self, node_id, name):
        return self._attribute[node_id][name]

    def is_cyclic(self):
        has_cycle = [False]

        def on_back_edge():
            has_cycle[0] = True

        self.dfs(on_back_edge = on_back_edge)
        return has_cycle[0]

    def topo_sort(self):
        result = list()

        def on_finish(node):
            result.append(node)

        self.dfs(on_finish=on_finish)
        return list(reversed(result))

    def dfs(self, vertex_sequence=None, on_main_visit=None, on_visit=None, on_back_edge=None, on_finish=None):
        WHITE = 0
        GRAY  = 1
        BLACK = 2

        N = self.num_nodes()
        state = dict()
        for u in self._V:
            state[u] = WHITE

        def dfs_helper(source):
            if on_visit:
                on_visit(source)
            for v in self.out_nodes(source):
                if state[v] == WHITE:
                    state[v] = GRAY
                    dfs_helper(v)
                    state[v] = BLACK
                    if on_finish:
                        on_finish(v)
                elif state[v] == GRAY:
                    if on_back_edge:
                        on_back_edge()

        vertex_sequence = vertex_sequence or list(self._V)
        for v in vertex_sequence:
            if state[v] == WHITE:
                if on_main_visit:
                    on_main_visit(v)
                state[v] = GRAY
                dfs_helper(v)
                state[v] = BLACK
                if on_finish:
                    on_finish(v)
            assert(state[v] != GRAY)

    def scc(self):
        finish_time = dict()

        def on_finish(v):
            l = len(finish_time)
            finish_time[v] = l
        self.dfs(on_finish=on_finish)
        vertex_sequence = sorted(finish_time.keys(), key=lambda v: finish_time[v], reverse=True)

        scc_list = list()

        def on_main_visit(v):
            scc_list.append(list())

        def on_visit(v):
            scc_list[-1].append(v)

        transposed_g = self.transpose()
        transposed_g.dfs(vertex_sequence=vertex_sequence, on_main_visit=on_main_visit, on_visit=on_visit)

        return scc_list

    def write_to_dot(self, path, index_name_map=None):
        with open(path, "w") as fp:
          fp.write("digraph{\n")
          if index_name_map:
              for v in self._V:
                  fp.write("%d [label=\"%s\"]\n" % (v, index_name_map(v)))
          for v in self._V:
              for src in self.in_nodes(v):
                  fp.write("%d -> %d\n" % (src, v))
          fp.write("}\n")
