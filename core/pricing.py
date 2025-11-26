"""
Dynamic pricing engine for StreamBazaar
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from core.devices import device_manager


class PricingEngine:
    """Computes dynamic resource prices based on supply-demand dynamics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.price_history = {}
        self.smoothing_param = config.get('price_smoothing', 0.7)
        self.target_utilization = config.get('target_utilization', 0.8)
        self.over_utilization_aggressiveness = config.get('over_utilization_aggressiveness', 1.0)
        self.under_utilization_reduction = config.get('under_utilization_reduction', 0.5)
    
    def compute_base_price(self, resource_type: str, current_utilization: float, 
                          spot_price: float, previous_price: Optional[float] = None) -> float:
        """
        Compute the base price for a resource using exponential smoothing with demand-driven adjustments
        
        Args:
            resource_type: Type of resource (cpu, memory, network)
            current_utilization: Current utilization of the resource (0.0 to 1.0)
            spot_price: Current spot price computed from bids
            previous_price: Previous price for smoothing
            
        Returns:
            float: Computed base price
        """
        # If no previous price, use spot price as starting point
        if previous_price is None:
            previous_price = spot_price
            
        # Exponential smoothing
        smoothed_price = (self.smoothing_param * previous_price + 
                         (1 - self.smoothing_param) * spot_price)
        
        # Adjustment based on utilization
        adjustment = self._compute_utilization_adjustment(current_utilization)
        
        return smoothed_price * adjustment
    
    def _compute_utilization_adjustment(self, utilization: float) -> float:
        """
        Compute price adjustment based on utilization
        
        Args:
            utilization: Current utilization (0.0 to 1.0)
            
        Returns:
            float: Adjustment factor
        """
        if utilization > self.target_utilization:
            # Price increases when over-utilized
            excess = utilization - self.target_utilization
            return 1.0 + self.over_utilization_aggressiveness * (excess ** 2)
        else:
            # Price decreases when under-utilized
            deficit = self.target_utilization - utilization
            return 1.0 - self.under_utilization_reduction * deficit
    
    def compute_device_price(self, device_name: str, utilizations: Dict[str, float]) -> Dict[str, float]:
        """
        Compute prices for all resources of a device
        
        Args:
            device_name: Name of the device
            utilizations: Dictionary of resource utilizations {resource_type: utilization}
            
        Returns:
            Dict[str, float]: Prices for each resource type
        """
        device = device_manager.get_device(device_name)
        prices = {}
        
        for resource_type in device.base_price.keys():
            utilization = utilizations.get(resource_type, 0.0)
            base_price = device.calculate_resource_price(resource_type)
            prices[resource_type] = self.compute_base_price(
                resource_type, utilization, base_price
            )
            
        return prices