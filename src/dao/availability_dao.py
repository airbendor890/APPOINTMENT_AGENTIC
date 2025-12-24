from .base_dao import BaseDAO
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

class AvailabilitySlot:
    def __init__(self, provider_id, date, start_time, end_time, 
                 status='available', slot_id=None, created_at=None):
        self.id = slot_id
        self.provider_id = provider_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.created_at = created_at

class AvailabilityDAO(BaseDAO):
    """Data Access Object for Availability Slot operations"""
    
    #  The functions that can be used as a TOOL right now, given a tag $---TOOL---$

    # $---TOOL---$
    def create(self, slot):
        """Create a new availability slot"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        

        try:
            cursor.execute('''
                INSERT INTO availability_slots (provider_id, date, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, %s)
            ''', (slot.provider_id, slot.date, slot.start_time, slot.end_time, slot.status))
            
            slot.id = cursor.lastrowid
            conn.commit()
            return slot
        finally:
            conn.close()

    # $---TOOL---$
    def get_slots_by_date_overlapping_time_range(
        self, date, start_time, end_time=None, status="available", service_name=None
    ):
        """
        Get availability slots that overlap with a given time range on a specific date,
        joined with users (provider_id → users.id).
        If service_name is provided, it will join with appointment_types (type_id → appointment_types.id)
        and filter by service_name (case-insensitive, partial match).
        """
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # If end_time not provided, default to start_time + 1 hour
        if not end_time:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.strftime("%H:%M")

        try:
            if service_name:
                cursor.execute(
                    """
                    SELECT s.*, u.name, u.email, u.phone, u.preferences, at.name AS service_name
                    FROM availability_slots s
                    JOIN users u ON s.provider_id = u.id
                    JOIN appointment_types at ON at.id = s.type_id
                    WHERE at.name ILIKE %s
                    AND s.date = %s
                    AND s.status = %s
                    AND (
                        (s.start_time >= %s AND s.start_time < %s) OR
                        (s.end_time > %s AND s.end_time <= %s) OR
                        (s.start_time <= %s AND s.end_time >= %s)
                    )
                    ORDER BY s.start_time
                    """,
                    (
                        f"%{service_name}%",
                        date,
                        status,
                        start_time,
                        end_time,
                        start_time,
                        end_time,
                        start_time,
                        end_time,
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT s.*, u.name, u.email, u.phone, u.preferences, at.name AS service_name
                    FROM availability_slots s
                    JOIN users u ON s.provider_id = u.id
                    JOIN appointment_types at ON at.id = s.type_id
                    WHERE s.date = %s
                    AND s.status = %s
                    AND (
                        (s.start_time >= %s AND s.start_time < %s) OR
                        (s.end_time > %s AND s.end_time <= %s) OR
                        (s.start_time <= %s AND s.end_time >= %s)
                    )
                    ORDER BY s.start_time
                    """,
                    (
                        date,
                        status,
                        start_time,
                        end_time,
                        start_time,
                        end_time,
                        start_time,
                        end_time,
                    ),
                )

            rows = cursor.fetchall()
            slots = []
            for row in rows:
                slots.append(
                    {
                        "slot_id": row["id"],
                        "provider_id": row["provider_id"],
                        "date": row["date"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "status": row["status"],
                        "provider_name": row["name"],
                        "provider_email": row["email"],
                        "provider_ph_no": row["phone"],
                        "provider_pref": row["preferences"],
                        "service_name": row["service_name"],
                    }
                )
            return slots
        finally:
            conn.close()




    def get_available_slots_by_provider(self, provider_id, start_date, end_date):
        """Get available slots for a provider within date range"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                SELECT * FROM availability_slots 
                WHERE provider_id = %s 
                AND date >= %s 
                AND date <= %s
                AND status = 'available'
                ORDER BY date, start_time
            ''', (provider_id, start_date, end_date))
            
            rows = cursor.fetchall()
            slots = []
            for row in rows:
                slots.append({
                    "slot_id": row['id'],
                    "provider_id": row['provider_id'],
                    "date": row['date'],
                    "start_time": row['start_time'],
                    "end_time": row['end_time'],
                    "status": row['status'],
                    "created_at": row['created_at']
                })
            return slots
        finally:
            conn.close()
    
    def update_slot_status(self, slot_id, status):
        """Update slot status (available, booked, blocked)"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                UPDATE availability_slots 
                SET status = %s 
                WHERE id = %s
            ''', (status, slot_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


# ----------------  More methods 

    def update(self, slot):
        """Update availability slot"""
        if not slot.id:
            return None
            
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('''
                UPDATE availability_slots 
                SET provider_id = %s, date = %s, start_time = %s, end_time = %s, status = %s
                WHERE id = %s
            ''', (slot.provider_id, slot.date, slot.start_time, slot.end_time, 
                  slot.status, slot.id))
            
            conn.commit()
            return slot if cursor.rowcount > 0 else None
        finally:
            conn.close()
    
    def delete(self, slot_id):
        """Delete availability slot by ID"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('DELETE FROM availability_slots WHERE id = %s', (slot_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_id(self, slot_id):
        """Get availability slot by ID"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM availability_slots WHERE id = %s', (slot_id,))
            row = cursor.fetchone()
            
            if row:
                return AvailabilitySlot(
                    slot_id=row['id'],
                    provider_id=row['provider_id'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    status=row['status'],
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def get_all(self):
        """Get all availability slots"""
        conn = self.get_connection()
        # cursor = conn.cursor()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM availability_slots')
            rows = cursor.fetchall()
            
            slots = []
            for row in rows:
                slots.append(AvailabilitySlot(
                    slot_id=row['id'],
                    provider_id=row['provider_id'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    status=row['status'],
                    created_at=row['created_at']
                ))
            return slots
        finally:
            conn.close()
    
