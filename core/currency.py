"""
Virtual currency system for StreamBazaar
"""

from typing import Dict, List
import numpy as np


class CurrencySystem:
    """Manages the virtual currency system for tenants"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.decay_rate = config.get('currency', {}).get('decay_rate', 0.05)
        self.base_allocation = config.get('currency', {}).get('base_allocation', 100.0)
        self.priority_weight_factor = config.get('currency', {}).get('priority_weight_factor', 1.0)
        self.utilization_reward_factor = config.get('currency', {}).get('utilization_reward_factor', 0.5)
        self.balances: Dict[str, float] = {}
        self.history: Dict[str, List[float]] = {}
    
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """
        Initialize a tenant with starting currency balance
        
        Args:
            tenant_id: ID of the tenant
            priority_weight: Priority weight for the tenant (higher = more important)
        """
        self.balances[tenant_id] = self.base_allocation * priority_weight
        if tenant_id not in self.history:
            self.history[tenant_id] = []
        self.history[tenant_id].append(self.balances[tenant_id])
    
    def apply_decay(self):
        """Apply currency decay to all tenants to prevent hoarding"""
        for tenant_id in self.balances:
            self.balances[tenant_id] *= (1.0 - self.decay_rate)
            self.history[tenant_id].append(self.balances[tenant_id])
    
    def allocate_currency(self, tenant_id: str, priority_weight: float, 
                         avg_utilization: float, total_utilization: float):
        """
        Allocate currency to a tenant based on priority and utilization
        
        Args:
            tenant_id: ID of the tenant
            priority_weight: Priority weight for the tenant
            avg_utilization: Tenant's average resource utilization
            total_utilization: Total cluster utilization
        """
        # Calculate utilization reward factor
        utilization_reward = 0.0
        if total_utilization > 0:
            utilization_reward = self.utilization_reward_factor * (avg_utilization / total_utilization)
        
        # Calculate allocation amount
        allocation = self.base_allocation * (priority_weight + utilization_reward)
        
        # Add to tenant's balance
        if tenant_id not in self.balances:
            self.balances[tenant_id] = 0.0
        self.balances[tenant_id] += allocation
        
        # Record in history
        if tenant_id not in self.history:
            self.history[tenant_id] = []
        self.history[tenant_id].append(self.balances[tenant_id])
    
    def deduct_balance(self, tenant_id: str, amount: float) -> bool:
        """
        Deduct currency from a tenant's balance
        
        Args:
            tenant_id: ID of the tenant
            amount: Amount to deduct
            
        Returns:
            bool: True if deduction was successful, False if insufficient balance
        """
        if self.balances.get(tenant_id, 0) >= amount:
            self.balances[tenant_id] -= amount
            if tenant_id in self.history:
                self.history[tenant_id].append(self.balances[tenant_id])
            else:
                self.history[tenant_id] = [self.balances[tenant_id]]
            return True
        return False
    
    def get_balance(self, tenant_id: str) -> float:
        """Get the current balance for a tenant"""
        return self.balances.get(tenant_id, 0.0)
    
    def get_history(self, tenant_id: str) -> List[float]:
        """Get the balance history for a tenant"""
        return self.history.get(tenant_id, []).copy()