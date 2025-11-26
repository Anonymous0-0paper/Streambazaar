"""
Continuous double auction mechanism for StreamBazaar
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.devices import Device


@dataclass
class Bid:
    """Represents a bid from a tenant for resources"""
    tenant_id: str
    resource_bundle: Dict[str, float]  # {resource_type: amount}
    valuation: float  # How much the tenant values this bundle
    timestamp: float


@dataclass
class Allocation:
    """Represents an allocation of resources to a tenant"""
    tenant_id: str
    resource_bundle: Dict[str, float]
    price_paid: float
    timestamp: float


class AuctionMechanism:
    """Implements the continuous double auction mechanism"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.auction_interval = config.get('auction_interval', 1.0)
        self.min_bid_increment = config.get('min_bid_increment', 0.01)
        self.backpressure_sensitivity = config.get('backpressure_sensitivity', 2.0)
        
    def formulate_bid(self, tenant_id: str, operator_id: str, 
                     base_resources: Dict[str, float], 
                     current_input_rate: float, reference_input_rate: float,
                     processing_complexity: float, current_queue_length: float,
                     max_queue_length: float, timestamp: float) -> Bid:
        """
        Formulate a bid based on resource requirements and urgency factors
        
        Args:
            tenant_id: ID of the tenant submitting the bid
            operator_id: ID of the operator requiring resources
            base_resources: Base resource requirements {resource_type: amount}
            current_input_rate: Current input rate for the operator
            reference_input_rate: Reference input rate for baseline measurement
            processing_complexity: Operator's sensitivity to input rate variations (0-1)
            current_queue_length: Current queue length upstream of operator
            max_queue_length: Maximum queue capacity
            timestamp: Current time
            
        Returns:
            Bid: Formulated bid
        """
        # Calculate actual resource requirements based on input rate
        actual_resources = {}
        rate_ratio = current_input_rate / reference_input_rate if reference_input_rate > 0 else 1.0
        
        for resource_type, base_amount in base_resources.items():
            actual_resources[resource_type] = base_amount * (1 + processing_complexity * rate_ratio)
        
        # Calculate base valuation
        base_valuation = sum(actual_resources.values())  # Simplified valuation
        
        # Calculate urgency factor based on backpressure
        queue_ratio = current_queue_length / max_queue_length if max_queue_length > 0 else 0.0
        urgency_factor = np.exp(self.backpressure_sensitivity * queue_ratio)
        
        # Final valuation includes urgency factor
        valuation = base_valuation * urgency_factor
        
        return Bid(
            tenant_id=tenant_id,
            resource_bundle=actual_resources,
            valuation=valuation,
            timestamp=timestamp
        )
    
    def determine_winners(self, bids: List[Bid], available_resources: Dict[str, float],
                         tenant_balances: Dict[str, float]) -> Tuple[List[Allocation], List[Bid]]:
        """
        Determine winners of the auction using greedy approximation
        
        Args:
            bids: List of bids submitted in this auction round
            available_resources: Available resources {resource_type: amount}
            tenant_balances: Current virtual currency balances {tenant_id: balance}
            
        Returns:
            Tuple[List[Allocation], List[Bid]]: Winning allocations and rejected bids
        """
        # Sort bids by efficiency (valuation/resource ratio)
        def calculate_efficiency(bid: Bid) -> float:
            total_resources = sum(bid.resource_bundle.values())
            if total_resources == 0:
                return 0.0
            return bid.valuation / total_resources
        
        sorted_bids = sorted(bids, key=calculate_efficiency, reverse=True)
        
        allocations = []
        rejected_bids = []
        remaining_resources = available_resources.copy()
        
        for bid in sorted_bids:
            # Check if tenant has enough balance
            if tenant_balances.get(bid.tenant_id, 0) < bid.valuation:
                rejected_bids.append(bid)
                continue
            
            # Check if resources are available
            can_allocate = True
            for resource_type, amount in bid.resource_bundle.items():
                if remaining_resources.get(resource_type, 0) < amount:
                    can_allocate = False
                    break
            
            if can_allocate:
                # Allocate resources
                allocation = Allocation(
                    tenant_id=bid.tenant_id,
                    resource_bundle=bid.resource_bundle,
                    price_paid=bid.valuation,
                    timestamp=bid.timestamp
                )
                allocations.append(allocation)
                
                # Update remaining resources
                for resource_type, amount in bid.resource_bundle.items():
                    remaining_resources[resource_type] -= amount
                
                # Deduct from tenant balance
                tenant_balances[bid.tenant_id] -= bid.valuation
            else:
                rejected_bids.append(bid)
        
        return allocations, rejected_bids