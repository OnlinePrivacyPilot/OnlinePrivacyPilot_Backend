from src import footprint
from simple_graph_sqlite import database as db
from simple_graph_sqlite.visualizers import graphviz_visualize
from typing import Optional
from sqlite3 import IntegrityError
import unicodedata
import string

class Storage:
    def __new__(cls, target: str = None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
            cls.footprint_id = 0
            cls.db_file = cls.get_filename(target)
            cls.db_conn = db.initialize(cls.db_file)
        return cls.instance

    def get_filename(target: str) -> str:
        """
        This method uses target value to generate a name for the DB file

        Args:
            target (str): Input target

        Returns:
            str: Name for DB file
        """
        filename = unicodedata.normalize('NFKD', target).encode('ASCII', 'ignore').decode()
        return ''.join(char for char in filename if char in "-_ ().%s%s" % (string.digits, string.ascii_letters))
    
    def store_graph(self, fp: footprint.Footprint = None, source_footprint_id: int = None) -> None:
        """ This method stores recursively whole given fingerprint by calling `store_node()` and `store_edge`

        Args:
            fp (footprint, optional): _description_. Defaults to None.
            source_footprint_id (int, optional): _description_. Defaults to None.
        """
        if isinstance(fp, footprint.Footprint):
            footprint_id = self.store_node(fp.method, fp.target_type, fp.target)
            if source_footprint_id:
                self.store_edge(source_footprint_id, footprint_id)
            if fp.children_footprints:
                for child_footprint in fp.children_footprints:
                    self.store_graph(child_footprint, footprint_id)

    def store_node(self, method: str, type: str, value: str) -> int:
        """
        This method stores a footprint in the graph.

        Args:
            method (str): Method used to retieve footprint
            type (str): Type of footprint
            value (str): Value of footprint

        Returns:
            int: ID corresponding to stored node
        """
        self.footprint_id += 1
        try:
            db.atomic(self.db_file, db.add_node({'method': method, 'type': type, 'value': value}, self.footprint_id))
        except IntegrityError:
            db.atomic(self.db_file, db.remove_nodes(db.traverse(self.db_file, 1, neighbors_fn=db.find_neighbors)))
            db.atomic(self.db_file, db.add_node({'method': method, 'type': type, 'value': value}, self.footprint_id))
        return self.footprint_id

    def store_edge(self, parent_id: int, child_id: int) -> None:
        """
        This method stores an edge in the graph.

        Args:
            parent_id (int): Parent node ID
            child_id (int): Child node ID
        """
        db.atomic(self.db_file, db.connect_nodes(parent_id, child_id, {}))
    
    def delete_node(self, id: int) -> None:
        """
        This method deletes a node according to its ID, all child nodes will be also deleted.

        Args:
            id (int): ID of the node to delete
        """
        db.atomic(self.db_file, db.remove_nodes(db.traverse(self.db_file, id, neighbors_fn=db.find_outbound_neighbors)))
 

    def gen_graphviz(self):
        graphviz_visualize(self.db_file, self.db_file+'.dot', db.traverse(self.db_file, 1, neighbors_fn=db.find_neighbors))
