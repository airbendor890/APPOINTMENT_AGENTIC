from .base_dao import BaseDAO
import psycopg2
import psycopg2.extras

class Service:
    def __init__(self, provider_id, name, duration_minutes, price, service_id=None):
        self.id = service_id
        self.provider_id = provider_id
        self.name = name
        self.duration_minutes = duration_minutes
        self.price = price

class ServiceDAO(BaseDAO):
    """Data Access Object for Service operations"""
    
    def create(self, service):
        """Create a new service"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO services (provider_id, name, duration_minutes, price)
                VALUES (%s, %s, %s, %s)
            ''', (service.provider_id, service.name, service.duration_minutes, service.price))
            
            service.id = cursor.lastrowid
            conn.commit()
            return service
        finally:
            conn.close()
    
    def get_by_id(self, service_id):
        """Get service by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM services WHERE id = %s', (service_id,))
            row = cursor.fetchone()
            
            if row:
                return Service(
                    service_id=row['id'],
                    provider_id=row['provider_id'],
                    name=row['name'],
                    duration_minutes=row['duration_minutes'],
                    price=row['price']
                )
            return None
        finally:
            conn.close()
    
    def get_all(self):
        """Get all services"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM services')
            rows = cursor.fetchall()
            
            services = []
            for row in rows:
                services.append(Service(
                    service_id=row['id'],
                    provider_id=row['provider_id'],
                    name=row['name'],
                    duration_minutes=row['duration_minutes'],
                    price=row['price']
                ))
            return services
        finally:
            conn.close()

    def get_all_service_names(self):
        """Get all services"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            cursor.execute('SELECT * FROM appointment_types')
            rows = cursor.fetchall()
            
            services = []
            for row in rows:
                services.append(
                    row['name'])
            return services
        finally:
            conn.close()

    def update(self, service):
        """Update service information"""
        if not service.id:
            return None
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE services 
                SET provider_id = %s, name = %s, duration_minutes = %s, price = %s
                WHERE id = %s
            ''', (service.provider_id, service.name, service.duration_minutes, 
                  service.price, service.id))
            
            conn.commit()
            return service if cursor.rowcount > 0 else None
        finally:
            conn.close()
    
    def delete(self, service_id):
        """Delete service by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM services WHERE id = %s', (service_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_by_provider(self, provider_id):
        """Get all services for a specific provider"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM services WHERE provider_id = %s', (provider_id,))
            rows = cursor.fetchall()
            
            services = []
            for row in rows:
                services.append(Service(
                    service_id=row['id'],
                    provider_id=row['provider_id'],
                    name=row['name'],
                    duration_minutes=row['duration_minutes'],
                    price=row['price']
                ))
            return services
        finally:
            conn.close()
    
    def find_matching_services(self, service_type):
        """Find services that match the service type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT s.*, p.name as provider_name, p.email, p.location, p.specialties
                FROM services s
                JOIN providers p ON s.provider_id = p.id
                WHERE LOWER(s.name) LIKE %s OR LOWER(p.specialties) LIKE %s
            ''', (f'%{service_type.lower()}%', f'%{service_type.lower()}%'))
            
            rows = cursor.fetchall()
            services = []
            for row in rows:
                service_info = {
                    "service_id": row['id'],
                    "provider_id": row['provider_id'],
                    "provider_name": row['provider_name'],
                    "provider_email": row['email'],
                    "location": row['location'],
                    "specialties": row['specialties'],
                    "service_name": row['name'],
                    "duration_minutes": row['duration_minutes'],
                    "price": row['price']
                }
                services.append(service_info)
            return services
        finally:
            conn.close()
