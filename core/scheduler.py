"""
Main scheduler implementation for StreamBazaar
"""

import time
from typing import Dict, List, Tuple
from core.devices import DeviceManager, device_manager
from core.pricing import PricingEngine
from core.auction import AuctionMechanism, Bid, Allocation
from core.currency import CurrencySystem
from core.metrics import MetricsTracker


class StreamBazaarScheduler:
    """Main scheduler implementing the StreamBazaar system"""
    
    def __init__(self, hyperparameters: Dict):
        self.config = hyperparameters
        self.device_manager = device_manager
        self.pricing_engine = PricingEngine(hyperparameters.get('pricing', {}))
        self.auction_mechanism = AuctionMechanism(hyperparameters.get('auction', {}))
        self.currency_system = CurrencySystem(hyperparameters)
        self.metrics_tracker = MetricsTracker()
        
        # State tracking
        self.current_allocations: Dict[str, Allocation] = {}
        self.tenant_balances: Dict[str, float] = {}
        self.resource_utilizations: Dict[str, Dict[str, float]] = {}
        self.last_auction_time = time.time()
        
    def initialize_tenant(self, tenant_id: str, priority_weight: float = 1.0):
        """
        Initialize a tenant in the system
        
        Args:
            tenant_id: ID of the tenant
            priority_weight: Priority weight for the tenant
        """
        self.currency_system.initialize_tenant(tenant_id, priority_weight)
        self.tenant_balances[tenant_id] = self.currency_system.get_balance(tenant_id)
    
    def submit_bid(self, tenant_id: str, operator_id: str, 
                   base_resources: Dict[str, float], 
                   current_input_rate: float, reference_input_rate: float,
                   processing_complexity: float, current_queue_length: float,
                   max_queue_length: float) -> Bid:
        """
        Submit a bid for resources on behalf of a tenant
        
        Args:
            tenant_id: ID of the tenant
            operator_id: ID of the operator requiring resources
            base_resources: Base resource requirements
            current_input_rate: Current input rate for the operator
            reference_input_rate: Reference input rate for baseline measurement
            processing_complexity: Operator's sensitivity to input rate variations
            current_queue_length: Current queue length upstream of operator
            max_queue_length: Maximum queue capacity
            
        Returns:
            Bid: The formulated bid
        """
        bid = self.auction_mechanism.formulate_bid(
            tenant_id, operator_id, base_resources,
            current_input_rate, reference_input_rate,
            processing_complexity, current_queue_length,
            max_queue_length, time.time()
        )
        return bid
    
    def run_auction_round(self, bids: List[Bid], available_resources: Dict[str, float]) -> List[Allocation]:
        """
        Run a round of the auction mechanism
        
        Args:
            bids: List of bids to consider
            available_resources: Currently available resources
            
        Returns:
            List[Allocation]: Winning allocations
        """
        # Update tenant balances from currency system
        for tenant_id in self.tenant_balances:
            self.tenant_balances[tenant_id] = self.currency_system.get_balance(tenant_id)
        
        # Run auction
        allocations, rejected_bids = self.auction_mechanism.determine_winners(
            bids, available_resources, self.tenant_balances
        )
        
        # Update allocations and tenant balances
        for allocation in allocations:
            self.current_allocations[allocation.tenant_id] = allocation
            # Deduct payment from tenant balance
            self.currency_system.deduct_balance(allocation.tenant_id, allocation.price_paid)
            self.tenant_balances[allocation.tenant_id] = self.currency_system.get_balance(allocation.tenant_id)
        
        # Record auction results for metrics
        valuations = [bid.valuation for bid in bids]
        allocation_flags = [1 if bid.tenant_id in [a.tenant_id for a in allocations] else 0 for bid in bids]
        self.metrics_tracker.record_auction_results(valuations, allocation_flags)
        
        # Apply currency decay
        self.currency_system.apply_decay()
        
        # Update last auction time
        self.last_auction_time = time.time()
        
        return allocations
    
    def update_resource_utilization(self, device_name: str, utilizations: Dict[str, float]):
        """
        Update resource utilization metrics for a device
        
        Args:
            device_name: Name of the device
            utilizations: Resource utilizations {resource_type: utilization}
        """
        if device_name not in self.resource_utilizations:
            self.resource_utilizations[device_name] = {}
        self.resource_utilizations[device_name].update(utilizations)
        # Record for metrics
        self.metrics_tracker.record_resource_utilization(utilizations)
    
    def record_tenant_latency(self, tenant_id: str, latency: float, priority: str = "medium"):
        """
        Record latency for a tenant for metrics tracking
        
        Args:
            tenant_id: ID of the tenant
            latency: Latency value
            priority: Priority level of the tenant
        """
        self.metrics_tracker.record_latency(tenant_id, latency, priority)
    
    def record_throughput(self, throughput: float):
        """
        Record system throughput for metrics tracking
        
        Args:
            throughput: Throughput value
        """
        self.metrics_tracker.record_throughput(throughput)
    
    def record_migration_impact(self, impact: float):
        """
        Record migration impact for metrics tracking
        
        Args:
            impact: Impact value
        """
        self.metrics_tracker.record_migration_impact(impact)
    
    def get_device_prices(self, device_name: str) -> Dict[str, float]:
        """
        Get current prices for all resources of a device
        
        Args:
            device_name: Name of the device
            
        Returns:
            Dict[str, float]: Current prices for each resource type
        """
        if device_name not in self.resource_utilizations:
            # Return base prices if no utilization data
            device = self.device_manager.get_device(device_name)
            prices = {}
            for resource_type in device.base_price.keys():
                prices[resource_type] = device.calculate_resource_price(resource_type)
            return prices
        
        return self.pricing_engine.compute_device_price(
            device_name, self.resource_utilizations[device_name]
        )
    
    def get_evaluation_metrics(self) -> Dict[str, float]:
        """
        Get all evaluation metrics
        
        Returns:
            Dict[str, float]: All evaluation metrics
        """
        return self.metrics_tracker.get_all_metrics()