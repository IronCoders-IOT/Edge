"""Application service for managing authentication in the IAM context."""
from typing import Optional
from iam.domain.entities import Device
from iam.domain.services import AuthService
from iam.infrastructure.repositories import DeviceRepository


class AuthApplicationService:
    """Service for handling authentication operations in the IAM context."""
    def __init__(self):
        """Initialize the AuthApplicationService with necessary repositories and services."""
        self.device_repository = DeviceRepository()
        self.auth_service = AuthService()

    def register_device(self) -> Device:
        """Register a new device with automatically generated ID and API key.
        
        Returns:
            Device: The newly registered device with its credentials.
        """
        return self.device_repository.create_device()

    def authenticate(self, device_id: str, api_key: str):
        """authenticate a device using its ID and API key.

        Args:
            device_id (str): The unique identifier for the device.
            api_key (str): The API key associated with the device.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        device: Optional[Device] = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return self.auth_service.authenticate(device)

    def get_by_id_and_api_key(self, device_id: str, api_key: str) -> Optional[Device]:
        """get a device by its ID and API key.

        Args:
            device_id (str): The unique identifier for the device.
            api_key (str): The API key associated with the device

        Returns:
            Device: The device if found, otherwise None.
        """
        return self.device_repository.find_by_id_and_api_key(device_id, api_key)

    def get_or_create_test_device(self) -> Device:
        """Get or create a test device for development purposes.
        Returns:
            Device: A test device with a predefined ID and API key.
        """
        return self.device_repository.get_or_create_test_device()