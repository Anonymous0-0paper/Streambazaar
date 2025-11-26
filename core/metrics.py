"""
Metrics module for StreamBazaar evaluation
Implements all metrics mentioned in the paper
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from core.devices import device_manager


class MetricsTracker:
    """Tracks and computes evaluation metrics for StreamBazaar"""
    
    def __init__(self):
        # Metrics history
        self.resource_utilization_history: List[Dict[str, float]] = []
        self.latency_history: List[Dict[str, Dict[str, Any]]] = []
        self.valuations_history: List[List[float]] = []
        self.allocations_history: List[List[int]] = []
        self.throughput_history: List[float] = []
        self.migration_impact_history: List[float] = []
        
        # SLA requirements for high-priority applications
        self.sla_requirements: Dict[str, float] = {
            "high_priority_latency": 100.0  # ms
        }
    
    def record_resource_utilization(self, utilizations: Dict[str, float]):
        """Record resource utilization metrics"""
        self.resource_utilization_history.append(utilizations.copy())
    
    def record_latency(self, tenant_id: str, latency: float, priority: str = "medium"):
        """Record latency for a tenant"""
        if not self.latency_history:
            self.latency_history.append({})
        self.latency_history[-1][tenant_id] = {
            "latency": float(latency),
            "priority": priority
        }
    
    def record_auction_results(self, valuations: List[float], allocations: List[int]):
        """Record auction results for economic efficiency calculation"""
        self.valuations_history.append(valuations.copy())
        self.allocations_history.append(allocations.copy())
    
    def record_throughput(self, throughput: float):
        """Record system throughput"""
        self.throughput_history.append(float(throughput))
    
    def record_migration_impact(self, impact: float):
        """Record migration impact on performance"""
        self.migration_impact_history.append(float(impact))
    
    def calculate_resource_utilization_efficiency(self) -> float:
        """
        Resource Utilization Efficiency (RUE): 
        Average of CPU, memory, and network utilization
        """
        if not self.resource_utilization_history:
            return 0.0
        
        total_efficiency = 0.0
        count = len(self.resource_utilization_history)
        
        for utilizations in self.resource_utilization_history:
            # Average of CPU, memory, and network utilization
            avg_utilization = np.mean([
                utilizations.get("cpu", 0.0),
                utilizations.get("memory", 0.0),
                utilizations.get("network", 0.0)
            ])
            total_efficiency += float(avg_utilization)
        
        return float(total_efficiency / count) if count > 0 else 0.0
    
    def calculate_tail_latency_violation_rate(self) -> float:
        """
        Tail Latency Violation Rate (TLVR):
        Percentage of time windows where 99th percentile latency exceeds SLA
        """
        if not self.latency_history:
            return 0.0
        
        violations = 0
        total_measurements = 0
        
        for time_window in self.latency_history:
            for tenant_data in time_window.values():
                if tenant_data["priority"] == "high":
                    total_measurements += 1
                    if tenant_data["latency"] > self.sla_requirements["high_priority_latency"]:
                        violations += 1
        
        return float(violations / total_measurements * 100) if total_measurements > 0 else 0.0
    
    def calculate_economic_efficiency_index(self) -> float:
        """
        Economic Efficiency Index (EEI):
        Ratio of achieved social welfare to theoretical maximum
        EEI = (sum of v_i * x_i) / (sum of v_i)
        """
        if not self.valuations_history or not self.allocations_history:
            return 0.0
        
        total_social_welfare = 0.0
        total_maximum_welfare = 0.0
        
        for valuations, allocations in zip(self.valuations_history, self.allocations_history):
            # Calculate achieved social welfare (sum of v_i * x_i)
            for i, (valuation, allocation) in enumerate(zip(valuations, allocations)):
                total_social_welfare += valuation * allocation
            
            # Calculate theoretical maximum welfare (sum of v_i)
            total_maximum_welfare += sum(valuations)
        
        return float(total_social_welfare / total_maximum_welfare) if total_maximum_welfare > 0 else 0.0
    
    def calculate_jains_fairness_index(self) -> float:
        """
        Jain's Fairness Index:
        J = (sum of x_i)^2 / (n * sum of x_i^2)
        where x_i is the resource allocation for tenant i
        """
        if not self.allocations_history:
            return 1.0  # Perfect fairness if no allocations
        
        # Sum allocations for each tenant across all time windows
        tenant_allocations: Dict[int, float] = {}
        
        for allocations in self.allocations_history:
            for i, allocation in enumerate(allocations):
                if i not in tenant_allocations:
                    tenant_allocations[i] = 0.0
                tenant_allocations[i] += float(allocation)
        
        if not tenant_allocations:
            return 1.0
        
        allocation_values = list(tenant_allocations.values())
        n = len(allocation_values)
        
        sum_allocations = sum(allocation_values)
        sum_squared_allocations = sum(x * x for x in allocation_values)
        
        if sum_squared_allocations == 0:
            return 1.0
        
        return float((sum_allocations * sum_allocations) / (n * sum_squared_allocations))
    
    def calculate_normalized_throughput(self) -> float:
        """
        Normalized Throughput:
        T_actual / T_max
        """
        if not self.throughput_history:
            return 0.0
        
        actual_throughput = float(np.mean(self.throughput_history))
        # Assuming theoretical maximum is 1.0 for normalization
        max_throughput = 1.0
        
        return float(actual_throughput / max_throughput) if max_throughput > 0 else 0.0
    
    def calculate_fairness_performance_product(self) -> float:
        """
        Fairness-Performance Product (FPP):
        Product of Jain's fairness index and normalized throughput
        FPP = J × (T_actual / T_max)
        """
        jains_index = self.calculate_jains_fairness_index()
        normalized_throughput = self.calculate_normalized_throughput()
        
        return float(jains_index * normalized_throughput)
    
    def calculate_migration_impact_score(self) -> float:
        """
        Migration Impact Score (MIS):
        Average performance degradation during operator migrations
        """
        if not self.migration_impact_history:
            return 0.0
        
        return float(np.mean(self.migration_impact_history))
    
    def get_all_metrics(self) -> Dict[str, float]:
        """Get all metrics as a dictionary"""
        return {
            "Resource Utilization Efficiency (RUE)": self.calculate_resource_utilization_efficiency(),
            "Tail Latency Violation Rate (TLVR)": self.calculate_tail_latency_violation_rate(),
            "Economic Efficiency Index (EEI)": self.calculate_economic_efficiency_index(),
            "Jain's Fairness Index": self.calculate_jains_fairness_index(),
            "Normalized Throughput": self.calculate_normalized_throughput(),
            "Fairness-Performance Product (FPP)": self.calculate_fairness_performance_product(),
            "Migration Impact Score (MIS)": self.calculate_migration_impact_score()
        }