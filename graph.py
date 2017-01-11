import copy
""" Graph For Python"""
class Graph:
    def __init__(self):
        self._V = set()
        self._connect = dict()
        self._connect_inv = dict()

        # Add order is preserved
        self._connect_ordered = dict()
        self._connect_inv_ordered = dict()
        
        self._attribute = dict()

    def transpose(self) -> 'Graph':
        transposed_g = Graph()
        for v in self._V:
            for u in self.in_nodes(v):
                transposed_g.connect(v, u)
        transposed_g._attribute = copy.deepcopy(self._attribute)
        return transposed_g

    def sub_graph(self, vertexes) -> 'Graph':
        sub_g = Graph()
        sub_vertex = set(vertexes)
        for v in sub_vertex:
            if v not in self._V:
                raise RuntimeError("vertex " + str(v) + " does not exist in the graph")
            for u in self.in_nodes(v):
                if u in sub_vertex:
                    sub_g.connect(u, v)
            sub_g._attribute[v] = copy.deepcopy(self._attribute[v])
        return sub_g

    def nodes(self) -> set:
        return set(self._V)

    def in_nodes(self, node_id: int) -> set:
        return self._connect_inv[node_id]

    def out_nodes(self, node_id: int) -> set:
        return self._connect[node_id]

    def num_nodes(self):
        return len(self._V)

    def possibly_add_node(self, u):
        if u not in self._V:
            self._V.add(u)
            self._connect[u] = set()
            self._connect_inv[u] = set()
            self._connect_ordered[u] = list()
            self._connect_inv_ordered[u] = list()
            val = dict()
            val['in_degree'] = 0
            val['out_degree'] = 0
            self._attribute[u] = val

    def delete(self, node_id):
        assert(node_id in self._V)
        dependencies = self.in_nodes(node_id)
        succeeding = self.out_nodes(node_id)

        for u in dependencies:
            assert node_id in self.out_nodes(u)
            self.out_nodes(u).remove(node_id)

        for v in succeeding:
            assert node_id in self.in_nodes(v)
            self.in_nodes(v).remove(node_id)

        del self._connect[node_id]
        del self._connect_inv[node_id]
        del self._connect_ordered[node_id]
        del self._connect_inv_ordered[node_id]
        del self._attribute[node_id]
        self._V.remove(node_id)

    def connect(self, u, v):
        self.possibly_add_node(u)
        self.possibly_add_node(v)
        if v not in self._connect[u]:
            self._connect[u].add(v)
            self._connect_inv[v].add(u)
            self._connect_ordered[u].append(v)
            self._connect_inv_ordered[v].append(u)
            self._attribute[u]['out_degree'] += 1
            self._attribute[v]['in_degree'] += 1

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
