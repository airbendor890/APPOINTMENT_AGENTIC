from .database import Database
from .provider_dao import ProviderDAO
from .service_dao import ServiceDAO
from .availability_dao import AvailabilityDAO
from .appointment_dao import AppointmentDAO

class DAOFactory:
    """Factory class for creating DAO instances"""
    
    def __init__(self):
        self.database = Database()
        self._provider_dao = None
        self._service_dao = None
        self._availability_dao = None
        self._appointment_dao = None
    
    def get_provider_dao(self):
        """Get Provider DAO instance"""
        if self._provider_dao is None:
            self._provider_dao = ProviderDAO(self.database)
        return self._provider_dao
    
    def get_service_dao(self):
        """Get Service DAO instance"""
        if self._service_dao is None:
            self._service_dao = ServiceDAO(self.database)
        return self._service_dao
    
    def get_availability_dao(self):
        """Get Availability DAO instance"""
        if self._availability_dao is None:
            self._availability_dao = AvailabilityDAO(self.database)
        return self._availability_dao
    
    def get_appointment_dao(self):
        """Get Appointment DAO instance"""
        if self._appointment_dao is None:
            self._appointment_dao = AppointmentDAO(self.database)
        return self._appointment_dao
    
    def close_connections(self):
        """Close all database connections (if needed for cleanup)"""
        # In this simple implementation, connections are closed after each operation
        # This method is here for future extension if connection pooling is added
        pass
