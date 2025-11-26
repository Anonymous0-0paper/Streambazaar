"""
Baseline schedulers for comparison with StreamBazaar
Implements all baselines mentioned in the paper
"""

import numpy as np
from typing import Dict, List, Tuple
from core.scheduler import StreamBazaarScheduler
from core.metrics import MetricsTracker


class FlinkDefaultBaseline:
    """Flink-Default baseline: Native Flink scheduler with static slot allocation"""
    
    def __init__(self, hyperparameters: Dict):
        self.config = hyperparameters
        self.metrics_tracker = MetricsTracker()
        self.tenant_allocations = {}
        self.tenant_balances = {}
        
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """Initialize a tenant with static resource allocation"""
        # In Flink default, resources are statically allocated
        # We simulate this by giving each tenant a fixed share
        self.tenant_balances[tenant_id] = 100.0 * priority_weight
        
    def run_scheduling_round(self, tenant_requirements: Dict[str, Dict[str, float]], 
                            available_resources: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Run a scheduling round with static allocation"""
        allocations = {}
        remaining_resources = available_resources.copy()
        
        # Sort tenants by priority (higher priority weight first)
        sorted_tenants = sorted(
            tenant_requirements.items(), 
            key=lambda x: self.tenant_balances.get(x[0], 0), 
            reverse=True
        )
        
        # Allocate resources statically
        for tenant_id, requirements in sorted_tenants:
            allocation = {}
            for resource_type, required_amount in requirements.items():
                # Allocate minimum of what's required and what's available
                allocated_amount = min(required_amount, remaining_resources.get(resource_type, 0))
                allocation[resource_type] = allocated_amount
                remaining_resources[resource_type] = remaining_resources.get(resource_type, 0) - allocated_amount
            
            allocations[tenant_id] = allocation
            
            # Record for metrics
            total_required = sum(requirements.values())
            total_allocated = sum(allocation.values())
            efficiency = total_allocated / total_required if total_required > 0 else 0
            self.metrics_tracker.record_auction_results([total_required], [1 if efficiency > 0.5 else 0])
        
        return allocations
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """Get evaluation metrics"""
        return self.metrics_tracker.get_all_metrics()


class DS2Baseline:
    """DS2 baseline: Auto-scaling approach"""
    
    def __init__(self, hyperparameters: Dict):
        self.config = hyperparameters
        self.metrics_tracker = MetricsTracker()
        self.tenant_allocations = {}
        self.scaling_factor = 1.2  # Scaling factor for resource allocation
        
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """Initialize a tenant"""
        pass  # DS2 doesn't use virtual currency system
        
    def run_scheduling_round(self, tenant_requirements: Dict[str, Dict[str, float]], 
                            available_resources: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Run a scheduling round with dynamic scaling"""
        allocations = {}
        remaining_resources = available_resources.copy()
        
        # DS2 scales resources based on demand
        for tenant_id, requirements in tenant_requirements.items():
            allocation = {}
            for resource_type, required_amount in requirements.items():
                # Scale the allocation based on demand
                scaled_amount = min(required_amount * self.scaling_factor, remaining_resources.get(resource_type, 0))
                allocation[resource_type] = scaled_amount
                remaining_resources[resource_type] = remaining_resources.get(resource_type, 0) - scaled_amount
            
            allocations[tenant_id] = allocation
            
            # Record for metrics
            total_required = sum(requirements.values())
            total_allocated = sum(allocation.values())
            self.metrics_tracker.record_auction_results([total_required], [1 if total_allocated > 0 else 0])
        
        return allocations
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """Get evaluation metrics"""
        return self.metrics_tracker.get_all_metrics()


class CAPSysBaseline:
    """CAPSys baseline: Contention-aware placement strategy"""
    
    def __init__(self, hyperparameters: Dict):
        self.config = hyperparameters
        self.metrics_tracker = MetricsTracker()
        self.resource_contention = {}  # Track resource contention
        
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """Initialize a tenant"""
        pass
        
    def run_scheduling_round(self, tenant_requirements: Dict[str, Dict[str, float]], 
                            available_resources: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Run a scheduling round with contention awareness"""
        allocations = {}
        remaining_resources = available_resources.copy()
        
        # CAPSys considers resource contention
        for tenant_id, requirements in tenant_requirements.items():
            allocation = {}
            contention_factor = 1.0  # Default factor
            
            # Adjust allocation based on resource contention
            for resource_type, required_amount in requirements.items():
                # Simulate contention effect
                if resource_type in self.resource_contention:
                    contention_factor = 1.0 - (self.resource_contention[resource_type] * 0.3)
                
                # Allocate resources considering contention
                allocated_amount = min(required_amount * contention_factor, remaining_resources.get(resource_type, 0))
                allocation[resource_type] = allocated_amount
                remaining_resources[resource_type] = remaining_resources.get(resource_type, 0) - allocated_amount
                
                # Update contention
                if resource_type not in self.resource_contention:
                    self.resource_contention[resource_type] = 0.0
                self.resource_contention[resource_type] += 0.1 * (required_amount / available_resources.get(resource_type, 1.0))
            
            allocations[tenant_id] = allocation
            
            # Record for metrics
            total_required = sum(requirements.values())
            total_allocated = sum(allocation.values())
            self.metrics_tracker.record_auction_results([total_required], [1 if total_allocated > 0 else 0])
        
        return allocations
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """Get evaluation metrics"""
        return self.metrics_tracker.get_all_metrics()


class TALOSBaseline:
    """TALOS baseline: Task-level autoscaler"""
    
    def __init__(self, hyperparameters: Dict):
        self.config = hyperparameters
        self.metrics_tracker = MetricsTracker()
        self.task_monitoring = {}  # Track individual tasks
        
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """Initialize a tenant"""
        self.task_monitoring[tenant_id] = {
            "tasks": {},
            "over_provisioning": 0.0
        }
        
    def run_scheduling_round(self, tenant_requirements: Dict[str, Dict[str, float]], 
                            available_resources: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Run a scheduling round with task-level monitoring"""
        allocations = {}
        remaining_resources = available_resources.copy()
        
        # TALOS monitors individual tasks to minimize over-provisioning
        for tenant_id, requirements in tenant_requirements.items():
            allocation = {}
            over_provisioning_factor = 0.9  # Reduce over-provisioning
            
            # Allocate resources with reduced over-provisioning
            for resource_type, required_amount in requirements.items():
                # Reduce allocation to minimize over-provisioning
                allocated_amount = min(required_amount * over_provisioning_factor, remaining_resources.get(resource_type, 0))
                allocation[resource_type] = allocated_amount
                remaining_resources[resource_type] = remaining_resources.get(resource_type, 0) - allocated_amount
            
            allocations[tenant_id] = allocation
            
            # Record for metrics
            total_required = sum(requirements.values())
            total_allocated = sum(allocation.values())
            self.metrics_tracker.record_auction_results([total_required], [1 if total_allocated > 0 else 0])
            
            # Update over-provisioning metric
            if tenant_id in self.task_monitoring:
                self.task_monitoring[tenant_id]["over_provisioning"] = max(0, 1.0 - (total_allocated / total_required)) if total_required > 0 else 0
        
        return allocations
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """Get evaluation metrics"""
        return self.metrics_tracker.get_all_metrics()