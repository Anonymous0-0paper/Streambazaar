"""
Device definitions and power/price calculations for StreamBazaar
"""

import yaml
import os
from typing import Dict, Any


class Device:
    """Represents a computing device with resource specifications and pricing"""
    
    def __init__(self, name: str, category: str, resources: Dict[str, float], 
                 base_price: Dict[str, float], power_consumption: float):
        self.name = name
        self.category = category
        self.resources = resources
        self.base_price = base_price
        self.power_consumption = power_consumption
    
    def calculate_power_cost(self, time_hours: float, cost_per_kwh: float = 0.15) -> float:
        """Calculate the power cost for running this device for a given time"""
        # Convert watts to kWh and multiply by cost
        kwh = (self.power_consumption * time_hours) / 1000.0
        return kwh * cost_per_kwh
    
    def calculate_resource_price(self, resource_type: str, utilization: float = 1.0) -> float:
        """Calculate the price for a resource based on utilization"""
        if resource_type not in self.base_price:
            raise ValueError(f"Resource type {resource_type} not defined for device {self.name}")
        
        base = self.base_price[resource_type]
        # Simple pricing model - increase price with utilization
        return base * (1.0 + 0.5 * utilization)


class DeviceManager:
    """Manages all devices in the system"""
    
    def __init__(self, config_path: str = "config/devices.yaml"):
        self.devices: Dict[str, Device] = {}
        self.load_devices(config_path)
    
    def load_devices(self, config_path: str):
        """Load device definitions from YAML configuration"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Device configuration file not found: {config_path}")
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        for device_name, device_data in config.get('devices', {}).items():
            device = Device(
                name=device_name,
                category=device_data['category'],
                resources=device_data['resources'],
                base_price=device_data['base_price'],
                power_consumption=device_data['power_consumption']
            )
            self.devices[device_name] = device
    
    def get_device(self, name: str) -> Device:
        """Get a device by name"""
        if name not in self.devices:
            raise ValueError(f"Device {name} not found")
        return self.devices[name]
    
    def list_devices(self) -> Dict[str, Device]:
        """Get all devices"""
        return self.devices.copy()


# Global device manager instance
device_manager = DeviceManager()