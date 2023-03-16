from simple_graph_sqlite import database as db
from simple_graph_sqlite.visualizers import graphviz_visualize
from typing import Optional
from sqlite3 import IntegrityError

class Storage:
    def __new__(cls, db_file: Optional[str] = None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
            cls.footprint_id = 0
            cls.db_file = db_file
            cls.db_conn = db.initialize(cls.db_file)
        return cls.instance

    def store_node(self, method: str, type: str, value: str) -> int:
        """
        In that function we store a node in the graph.

        :return: int
        """
        self.footprint_id += 1
        try:
            db.atomic(self.db_file, db.add_node({'method': method, 'type': type, 'value': value}, self.footprint_id))
        except IntegrityError:
            db.atomic(self.db_file, db.remove_nodes(db.traverse(self.db_file, 1, neighbors_fn=db.find_neighbors)))
            db.atomic(self.db_file, db.add_node({'method': method, 'type': type, 'value': value}, self.footprint_id))
        return self.footprint_id

    def store_edge(self, parent_id, child_id) -> None:
        """
        In that function we store an edge in the graph.

        :return: None
        """
        db.atomic(self.db_file, db.connect_nodes(parent_id, child_id, {}))