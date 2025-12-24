from .base_dao import BaseDAO

class Provider:
    def __init__(self, name, email, location=None, specialties=None, provider_id=None):
        self.id = provider_id
        self.name = name
        self.email = email
        self.location = location
        self.specialties = specialties

class ProviderDAO(BaseDAO):
    """Data Access Object for Provider operations"""
    
    def create(self, provider):
        """Create a new provider"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO providers (name, email, location, specialties)
                VALUES (%s, %s, %s, %s)
            ''', (provider.name, provider.email, provider.location, provider.specialties))
            
            provider.id = cursor.lastrowid
            conn.commit()
            return provider
        finally:
            conn.close()
    
    def get_by_id(self, provider_id):
        """Get provider by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM providers WHERE id = %s', (provider_id,))
            row = cursor.fetchone()
            
            if row:
                return Provider(
                    provider_id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    location=row['location'],
                    specialties=row['specialties']
                )
            return None
        finally:
            conn.close()
    
    def get_all(self):
        """Get all providers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM providers')
            rows = cursor.fetchall()
            
            providers = []
            for row in rows:
                providers.append(Provider(
                    provider_id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    location=row['location'],
                    specialties=row['specialties']
                ))
            return providers
        finally:
            conn.close()
    
    def update(self, provider):
        """Update provider information"""
        if not provider.id:
            return None
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE providers 
                SET name = %s, email = %s, location = %s, specialties = %s
                WHERE id = %s
            ''', (provider.name, provider.email, provider.location, 
                  provider.specialties, provider.id))
            
            conn.commit()
            return provider if cursor.rowcount > 0 else None
        finally:
            conn.close()
    
    def delete(self, provider_id):
        """Delete provider by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM providers WHERE id = %s', (provider_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def find_by_service_type(self, service_type):
        """Find providers who offer a specific service type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT DISTINCT p.* FROM providers p
                JOIN services s ON p.id = s.provider_id
                WHERE LOWER(s.name) LIKE %s OR LOWER(p.specialties) LIKE %s
            ''', (f'%{service_type.lower()}%', f'%{service_type.lower()}%'))
            
            rows = cursor.fetchall()
            providers = []
            for row in rows:
                providers.append(Provider(
                    provider_id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    location=row['location'],
                    specialties=row['specialties']
                ))
            return providers
        finally:
            conn.close()
