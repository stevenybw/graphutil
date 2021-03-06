import unittest
from graph import Graph

class TestGraph(unittest.TestCase):
    def test_basic(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(1, 3)
        g.connect(1, 4)
        g.connect(1, 5)
        g.connect(2, 6)

        self.assertSetEqual(set(g.out_nodes(1)), {2,3,4,5})
        self.assertSetEqual(set(g.out_nodes(2)), {6})
        self.assertEqual([e.dst for e in g.out_edges(1)], [2, 3, 4, 5])
        self.assertEqual([e.src for e in g.out_edges(1)], [1, 1, 1, 1])
        self.assertEqual([e.dst for e in g.in_edges(1)], [])
        self.assertEqual([e.src for e in g.in_edges(1)], [])

        self.assertEqual([e.dst for e in g.out_edges(2)], [6])
        self.assertEqual([e.src for e in g.out_edges(2)], [2])
        self.assertEqual([e.dst for e in g.in_edges(2)], [2])
        self.assertEqual([e.src for e in g.in_edges(2)], [1])

        for i in range(3,7):
            self.assertSetEqual(set(g.out_nodes(i)), set())
        self.assertEqual(g.num_nodes(), 6)

    def test_cyclic(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(1, 3)
        g.connect(1, 4)
        g.connect(1, 5)
        g.connect(2, 6)
        self.assertEqual(g.is_cyclic(), False)

        g = Graph()
        g.connect(1, 2)
        g.connect(1, 3)
        g.connect(1, 4)
        g.connect(1, 5)
        g.connect(2, 6)
        g.connect(6, 1)
        self.assertEqual(g.is_cyclic(), True)

    def test_topo_sort(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(1, 3)
        g.connect(2, 4)
        g.connect(3, 4)
        l = g.topo_sort()
        self.assertEqual(len(l), 4)
        print("TopoSort Result:", l)

    def test_scc_1(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(2, 1)
        g.connect(1, 3)
        g.connect(3, 1)
        g.connect(3, 4)
        g.connect(4, 3)

        g.connect(5, 6)
        g.connect(6, 5)
        g.connect(6, 7)
        g.connect(7, 6)

        correct_scc = {(1,2,3,4), (5,6,7)}

        scc_list = g.scc()
        self.assertEqual(len(scc_list), len(correct_scc))
        for scc in scc_list:
            self.assertIn(tuple(sorted(scc)), correct_scc)


    def test_scc_2(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(2, 1)
        g.connect(1, 3)
        g.connect(3, 1)
        g.connect(3, 4)
        g.connect(4, 3)

        g.connect(5, 6)
        g.connect(6, 5)
        g.connect(6, 7)
        g.connect(7, 6)

        g.connect(4, 7)
        g.connect(7, 4)

        correct_scc = {(1, 2, 3, 4, 5, 6, 7)}

        scc_list = g.scc()
        self.assertEqual(len(scc_list), len(correct_scc))
        for scc in scc_list:
            self.assertIn(tuple(sorted(scc)), correct_scc)

    def test_sub_graph(self):
        g = Graph()
        g.connect(1, 2)
        g.connect(2, 1)
        g.connect(1, 3)
        g.connect(3, 1)
        g.connect(3, 4)
        g.connect(4, 3)

        g.connect(5, 6)
        g.connect(6, 5)
        g.connect(6, 7)
        g.connect(7, 6)

        scc_list = g.scc()
        for scc in scc_list:
            sub_g = g.sub_graph(scc)
            self.assertEqual(sub_g.nodes(), set(scc))
            for v in sub_g.nodes():
                for u in sub_g.in_nodes(v):
                    self.assertIn(u, g.in_nodes(v))
        print("SCC Passed")

    def test_preserve_order(self):
        g = Graph()
        g.connect(4, 3)
        g.connect(1, 3)
        g.connect(2, 3)
        self.assertListEqual(g.in_nodes(3), [4,1,2])

        g = Graph()
        g.connect(1, 3)
        g.connect(2, 3)
        g.connect(4, 3)
        self.assertListEqual(g.in_nodes(3), [1,2,4])

        g = Graph()
        g.connect(1, 3)
        g.connect(2, 3)
        g.connect(4, 3)

        g.connect(3, 13)
        g.connect(3, 11)
        g.connect(3, 12)
        self.assertListEqual(g.in_nodes(3), [1, 2, 4])
        self.assertListEqual(g.out_nodes(3), [13, 11, 12])

        print("Preserve order passed")


if __name__ == 'main':
    unittest.main()
