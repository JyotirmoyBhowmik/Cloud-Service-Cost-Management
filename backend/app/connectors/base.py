"""
Base Cloud Connector Interface
Defines the standard contract for all multi-cloud adapters per User Request §13 and BBP §1285-1302.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class CloudConnector(ABC):
    """
    Standard interface that every cloud provider adapter must implement.
    Decouples core business logic from provider SDK implementations.
    """

    def __init__(self, connector_id: str, provider: str, config: Dict[str, Any]):
        self.connector_id = connector_id
        self.provider = provider
        self.config = config

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticates with the cloud provider IAM/OAuth endpoint."""
        pass

    @abstractmethod
    def validate_credentials(self) -> Dict[str, Any]:
        """Validates permission scopes and API access."""
        pass

    @abstractmethod
    def discover_hierarchy(self) -> List[Dict[str, Any]]:
        """Discovers native cloud organization/tenant/subscription/compartment tree."""
        pass

    @abstractmethod
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discovers provisioned cloud resources across configured scopes."""
        pass

    @abstractmethod
    def discover_services(self) -> List[Dict[str, Any]]:
        """Discovers cloud services active in the estate."""
        pass

    @abstractmethod
    def retrieve_pricing(self, service_codes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieves official rate catalog or retail price items."""
        pass

    @abstractmethod
    def retrieve_cost(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Retrieves billed and amortized cost records aligned with FOCUS 1.4."""
        pass

    @abstractmethod
    def retrieve_usage(self, resource_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieves operational telemetry and consumption metrics."""
        pass

    @abstractmethod
    def discover_dependencies(self) -> List[Dict[str, Any]]:
        """Discovers network or service topology relationships."""
        pass
