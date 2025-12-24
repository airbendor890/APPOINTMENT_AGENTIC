from .base_dao import BaseDAO
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

class Appointment:
    def __init__(self, type_id, seeker_id, provider_id, slot_id, scheduled_time, 
                 status='pending', notes='', appointment_id=None, created_at=None, updated_at=None):
        self.id = appointment_id
        self.type_id = type_id
        self.seeker_id = seeker_id
        self.provider_id = provider_id
        self.slot_id = slot_id
        self.scheduled_time = scheduled_time
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

#  The functions that can be used as a TOOL right now, given a tag $---TOOL---$
class AppointmentDAO(BaseDAO):
    """Data Access Object for Appointment operations"""
    
    # $---TOOL---$
    def create(self, appointment):
        """Create a new appointment"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                INSERT INTO appointments (
                    type_id, seeker_id, provider_id, slot_id, scheduled_time, status, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (appointment.type_id, appointment.seeker_id, appointment.provider_id,
                appointment.slot_id, appointment.scheduled_time, appointment.status,
                appointment.notes))
            
            # Fetch the generated primary key (Postgres way)
            appointment.id = cursor.fetchone()[0]

            conn.commit()
            return appointment
        finally:
            conn.close()


    
    def get_by_id(self, appointment_id):
        """Get appointment by ID"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM appointments WHERE id = %s', (appointment_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "appointment_id":row['id'],
                    "type_id":row['type_id'],
                    "seeker_id":row['seeker_id'],
                    "provider_id":row['provider_id'],
                    "slot_id":row['slot_id'],
                    "scheduled_time":row['scheduled_time'],
                    "status":row['status'],
                    "notes":row['notes'],
                    "created_at":row['created_at'],
                    "updated_at":row['updated_at']
                }
            return None
        finally:
            conn.close()
    
    def get_all(self):
        """Get all appointments"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM appointments ORDER BY scheduled_time')
            rows = cursor.fetchall()
            
            appointments = []
            for row in rows:
                appointments.append({
                    "appointment_id":row['id'],
                    "type_id":row['type_id'],
                    "seeker_id":row['seeker_id'],
                    "provider_id":row['provider_id'],
                    "slot_id":row['slot_id'],
                    "scheduled_time":row['scheduled_time'],
                    "status":row['status'],
                    "notes":row['notes'],
                    "created_at":row['created_at'],
                    "updated_at":row['updated_at']
                })
            return appointments
        finally:
            conn.close()
    
    def update(self, appointment_id, status):
        """Update appointment"""
        if not appointment_id:
            return None
            
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                UPDATE appointments 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (status, appointment_id))
            conn.commit()
            return True if cursor.rowcount > 0 else None
        finally:
            conn.close()
    
    def delete(self, appointment_id):
        """Delete appointment by ID"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('DELETE FROM appointments WHERE id = %s', (appointment_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_by_provider(self, provider_id, status=None):
        """Get appointments for a specific provider, optionally filter by status"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            if status:
                cursor.execute('''
                    SELECT * FROM appointments 
                    WHERE provider_id = %s AND status = %s
                    ORDER BY scheduled_time
                ''', (provider_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM appointments 
                    WHERE provider_id = %s
                    ORDER BY scheduled_time
                ''', (provider_id,))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append(Appointment(
                    appointment_id=row['id'],
                    type_id=row['type_id'],
                    seeker_id=row['seeker_id'],
                    provider_id=row['provider_id'],
                    slot_id=row['slot_id'],
                    scheduled_time=row['scheduled_time'],
                    status=row['status'],
                    notes=row['notes'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            return appointments
        finally:
            conn.close()
    
    def get_by_seeker(self, seeker_id, status=None):
        """Get appointments for a specific seeker, optionally filter by status"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            if status:
                cursor.execute('''
                    SELECT * FROM appointments 
                    WHERE seeker_id = %s AND status = %s
                    ORDER BY scheduled_time
                ''', (seeker_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM appointments 
                    WHERE seeker_id = %s
                    ORDER BY scheduled_time
                ''', (seeker_id,))
            
            rows = cursor.fetchall()
            appointments = []
            for row in rows:
                appointments.append(Appointment(
                    appointment_id=row['id'],
                    type_id=row['type_id'],
                    seeker_id=row['seeker_id'],
                    provider_id=row['provider_id'],
                    slot_id=row['slot_id'],
                    scheduled_time=row['scheduled_time'],
                    status=row['status'],
                    notes=row['notes'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            return appointments
        finally:
            conn.close()
    
    def update_status(self, appointment_id, new_status):
        """Update appointment status"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                UPDATE appointments 
                SET status = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            ''', (new_status, appointment_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_appointments_with_details(self, appointment_id=None):
        """Get appointment with full details including user names and slot info"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            query = '''
                SELECT a.*, 
                       seeker.name as seeker_name, seeker.email as seeker_email,
                       provider.name as provider_name, provider.email as provider_email,
                       slot.date as slot_date, slot.start_time, slot.end_time,
                       apt_type.name as appointment_type_name
                FROM appointments a
                JOIN users seeker ON a.seeker_id = seeker.id
                JOIN users provider ON a.provider_id = provider.id
                JOIN availability_slots slot ON a.slot_id = slot.id
                LEFT JOIN appointment_types apt_type ON a.type_id = apt_type.id
            '''
            
            if appointment_id:
                query += ' WHERE a.id = %s'
                cursor.execute(query, (appointment_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "appointment_id": row['id'],
                        "type_id": row['type_id'],
                        "appointment_type_name": row['appointment_type_name'],
                        "seeker_id": row['seeker_id'],
                        "seeker_name": row['seeker_name'],
                        "seeker_email": row['seeker_email'],
                        "provider_id": row['provider_id'],
                        "provider_name": row['provider_name'],
                        "provider_email": row['provider_email'],
                        "slot_id": row['slot_id'],
                        "slot_date": row['slot_date'],
                        "start_time": row['start_time'],
                        "end_time": row['end_time'],
                        "scheduled_time": row['scheduled_time'],
                        "status": row['status'],
                        "notes": row['notes'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                return None
            else:
                query += ' ORDER BY a.scheduled_time'
                cursor.execute(query)
                rows = cursor.fetchall()
                
                appointments = []
                for row in rows:
                    appointments.append({
                        "appointment_id": row['id'],
                        "type_id": row['type_id'],
                        "appointment_type_name": row['appointment_type_name'],
                        "seeker_id": row['seeker_id'],
                        "seeker_name": row['seeker_name'],
                        "seeker_email": row['seeker_email'],
                        "provider_id": row['provider_id'],
                        "provider_name": row['provider_name'],
                        "provider_email": row['provider_email'],
                        "slot_id": row['slot_id'],
                        "slot_date": row['slot_date'],
                        "start_time": row['start_time'],
                        "end_time": row['end_time'],
                        "scheduled_time": row['scheduled_time'],
                        "status": row['status'],
                        "notes": row['notes'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    })
                return appointments
        finally:
            conn.close()
