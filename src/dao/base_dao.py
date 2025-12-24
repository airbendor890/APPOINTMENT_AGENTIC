class BaseDAO:
    """Base class for all Data Access Objects"""
    
    def __init__(self, database):
        self.database = database
    
    def get_connection(self):
        """Get database connection from database manager"""
        return self.database.get_connection()
    
    def create(self, entity):
        raise NotImplementedError("Subclasses must implement create method")
    
    def get_by_id(self, entity_id):
        raise NotImplementedError("Subclasses must implement get_by_id method")
    
    def get_all(self):
        raise NotImplementedError("Subclasses must implement get_all method")
    
    def update(self, entity):
        raise NotImplementedError("Subclasses must implement update method")
    
    def delete(self, entity_id):
        raise NotImplementedError("Subclasses must implement delete method")
