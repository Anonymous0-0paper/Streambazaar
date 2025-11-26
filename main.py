"""
Main script to demonstrate StreamBazaar functionality
"""

import yaml
import numpy as np
from core.scheduler import StreamBazaarScheduler
from core.devices import device_manager
from core.baselines import FlinkDefaultBaseline, DS2Baseline, CAPSysBaseline, TALOSBaseline
from visualization.plotter import plotter
from evaluation.plots import generate_evaluation_plots, generate_application_comparison_plots
from evaluation.applications import app_simulator
from evaluation.scalability_evaluation import run_scalability_evaluation


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def simulate_streaming_cluster():
    """Simulate a streaming cluster with multiple tenants and devices"""
    # Load hyperparameters
    hyperparameters = load_config("config/hyperparameters.yaml")
    
    # Initialize scheduler
    scheduler = StreamBazaarScheduler(hyperparameters)
    
    # Initialize tenants
    tenants = {
        "tenant_1": {"priority": 1.5, "operators": ["op_1", "op_2"]},
        "tenant_2": {"priority": 1.0, "operators": ["op_3", "op_4", "op_5"]},
        "tenant_3": {"priority": 0.8, "operators": ["op_6"]}
    }
    
    for tenant_id, tenant_info in tenants.items():
        scheduler.initialize_tenant(tenant_id, tenant_info["priority"])
    
    # Get available devices
    devices = device_manager.list_devices()
    print(f"Available devices: {list(devices.keys())}")
    
    # Simulate several auction rounds
    for round_num in range(5):
        print(f"\n--- Auction Round {round_num + 1} ---")
        
        # Update resource utilizations
        for device_name in devices.keys():
            utilizations = {
                "cpu": np.random.uniform(0.5, 0.9),
                "memory": np.random.uniform(0.4, 0.8),
                "network": np.random.uniform(0.3, 0.7)
            }
            scheduler.update_resource_utilization(device_name, utilizations)
        
        # Submit bids from tenants
        bids = []
        for tenant_id, tenant_info in tenants.items():
            for op_id in tenant_info["operators"]:
                # Generate random resource requirements
                base_resources = {
                    "cpu": np.random.uniform(1, 4),
                    "memory": np.random.uniform(2, 8),
                    "network": np.random.uniform(0.5, 2)
                }
                
                # Generate random operational parameters
                current_input_rate = np.random.uniform(100, 1000)
                reference_input_rate = 500.0
                processing_complexity = np.random.uniform(0.1, 0.9)
                current_queue_length = np.random.uniform(0, 100)
                max_queue_length = 200.0
                
                # Submit bid
                bid = scheduler.submit_bid(
                    tenant_id, op_id, base_resources,
                    current_input_rate, reference_input_rate,
                    processing_complexity, current_queue_length,
                    max_queue_length
                )
                bids.append(bid)
        
        # Run auction
        available_resources = {
            "cpu": 32.0,
            "memory": 128.0,
            "network": 20.0
        }
        allocations = scheduler.run_auction_round(bids, available_resources)
        
        # Print results
        print(f"Number of bids: {len(bids)}")
        print(f"Number of allocations: {len(allocations)}")
        
        for allocation in allocations:
            print(f"  Tenant {allocation.tenant_id} allocated {allocation.resource_bundle} "
                  f"for ${allocation.price_paid:.2f}")
        
        # Print tenant balances
        print("Tenant balances:")
        for tenant_id in tenants.keys():
            balance = scheduler.currency_system.get_balance(tenant_id)
            print(f"  {tenant_id}: ${balance:.2f}")
    
    return scheduler


def create_sample_visualizations():
    """Create sample visualizations to demonstrate the plotting capabilities"""
    # Line plot example
    x = np.linspace(0, 10, 100).tolist()
    data = {
        "Tenant A": (x, np.sin(x).tolist()),
        "Tenant B": (x, np.cos(x).tolist()),
        "Tenant C": (x, np.sin(np.array(x) + np.pi/4).tolist())
    }
    
    fig1 = plotter.plot_line(
        data,
        "Resource Utilization Over Time",
        "Time (seconds)",
        "Utilization (%)",
        "utilization_over_time"
    )
    print("Created line plot: utilization_over_time")
    
    # Bar plot example
    data = {
        "CPU": [75.0, 65.0, 80.0],
        "Memory": [60.0, 70.0, 65.0],
        "Network": [45.0, 55.0, 50.0]
    }
    labels = ["Tenant A", "Tenant B", "Tenant C"]
    
    fig2 = plotter.plot_bar(
        data,
        labels,
        "Average Resource Utilization by Tenant",
        "Tenant",
        "Utilization (%)",
        "resource_utilization"
    )
    print("Created bar plot: resource_utilization")
    
    # Box plot example
    data = {
        "Tenant A": [np.random.normal(75, 5, 50).tolist(), np.random.normal(60, 7, 50).tolist()],
        "Tenant B": [np.random.normal(65, 6, 50).tolist(), np.random.normal(70, 4, 50).tolist()]
    }
    labels = ["CPU", "Memory"]
    
    fig3 = plotter.plot_box(
        data,
        labels,
        "Resource Utilization Distribution",
        "Resource Type",
        "Utilization (%)",
        "utilization_distribution"
    )
    print("Created box plot: utilization_distribution")


def run_baseline_comparison_evaluation():
    """Run evaluation comparing StreamBazaar with all baseline schedulers"""
    print("\n--- Running Baseline Comparison Evaluation ---")
    
    # Load hyperparameters
    hyperparameters = load_config("config/hyperparameters.yaml")
    
    # Initialize StreamBazaar scheduler
    streambazaar = StreamBazaarScheduler(hyperparameters)
    
    # Initialize baseline schedulers
    baselines = {
        "Flink-Default": FlinkDefaultBaseline(hyperparameters),
        "DS2": DS2Baseline(hyperparameters),
        "CAPSys": CAPSysBaseline(hyperparameters),
        "TALOS": TALOSBaseline(hyperparameters)
    }
    
    # Initialize tenants for all schedulers
    tenants = {
        "tenant_1": {"priority": 1.5, "operators": ["op_1", "op_2"]},
        "tenant_2": {"priority": 1.0, "operators": ["op_3", "op_4", "op_5"]},
        "tenant_3": {"priority": 0.8, "operators": ["op_6"]}
    }
    
    for tenant_id, tenant_info in tenants.items():
        streambazaar.initialize_tenant(tenant_id, tenant_info["priority"])
        for baseline in baselines.values():
            baseline.initialize_tenant(tenant_id, tenant_info["priority"])
    
    # Simulate several rounds for all schedulers
    for round_num in range(10):  # More rounds for better evaluation
        print(f"  Evaluation Round {round_num + 1}/10")
        
        # Generate tenant requirements for this round
        tenant_requirements = {}
        for tenant_id, tenant_info in tenants.items():
            requirements = {
                "cpu": np.random.uniform(2, 8) * len(tenant_info["operators"]),
                "memory": np.random.uniform(4, 16) * len(tenant_info["operators"]),
                "network": np.random.uniform(1, 4) * len(tenant_info["operators"])
            }
            tenant_requirements[tenant_id] = requirements
        
        # Available resources for this round
        available_resources = {
            "cpu": 32.0,
            "memory": 128.0,
            "network": 20.0
        }
        
        # Run StreamBazaar scheduling
        streambazaar.run_auction_round([], available_resources)  # Empty bids for simplicity
        
        # Run baseline scheduling
        for name, baseline in baselines.items():
            baseline.run_scheduling_round(tenant_requirements, available_resources)
    
    # Generate comparison plots
    all_schedulers = {"StreamBazaar": streambazaar}
    all_schedulers.update(baselines)
    plots = generate_evaluation_plots(streambazaar, baselines)
    
    print(f"Generated {len(plots)} baseline comparison plots:")
    for plot_name in plots:
        print(f"  - {plot_name}")


def run_application_comparison_evaluation():
    """Run evaluation comparing all schedulers across all applications"""
    print("\n--- Running Application Comparison Evaluation ---")
    
    # Load hyperparameters
    hyperparameters = load_config("config/hyperparameters.yaml")
    
    # Initialize all schedulers
    schedulers = {
        "StreamBazaar": StreamBazaarScheduler(hyperparameters),
        "Flink-Default": FlinkDefaultBaseline(hyperparameters),
        "DS2": DS2Baseline(hyperparameters),
        "CAPSys": CAPSysBaseline(hyperparameters),
        "TALOS": TALOSBaseline(hyperparameters)
    }
    
    # Get all applications
    applications = app_simulator.get_all_applications()
    app_names = list(applications.keys())
    
    print(f"Evaluating {len(app_names)} applications: {', '.join(app_names)}")
    
    # Simulate workloads for each application
    for app_name in app_names:
        print(f"  Evaluating {app_name}...")
        app = applications[app_name]
        
        # Initialize tenants for this application
        tenants = {
            f"tenant_{i+1}": {"priority": app.priority.value, "operators": [f"op_{j+1}" for j in range(app.num_operators)]}
            for i in range(3)  # 3 tenants per application
        }
        
        # Initialize all schedulers with tenants
        for scheduler in schedulers.values():
            for tenant_id, tenant_info in tenants.items():
                scheduler.initialize_tenant(tenant_id, tenant_info["priority"])
        
        # Simulate workload for multiple time steps
        for time_step in range(5):
            # Simulate tenant workloads for this application
            tenant_workloads = {}
            for tenant_id in tenants.keys():
                workload = app_simulator.simulate_tenant_workload(app_name, tenant_id, time_step)
                tenant_workloads[tenant_id] = workload
            
            # Run scheduling for all schedulers
            available_resources = {
                "cpu": 32.0,
                "memory": 128.0,
                "network": 20.0
            }
            
            # For simplicity, we'll just run the scheduling without detailed resource allocation
            for scheduler in schedulers.values():
                if hasattr(scheduler, 'run_auction_round'):
                    scheduler.run_auction_round([], available_resources)
                elif hasattr(scheduler, 'run_scheduling_round'):
                    # For baselines, create simplified requirements
                    requirements = {
                        tenant_id: workload["resource_requirements"]
                        for tenant_id, workload in tenant_workloads.items()
                    }
                    scheduler.run_scheduling_round(requirements, available_resources)
    
    # Generate application comparison plots
    plots = generate_application_comparison_plots(app_names, schedulers)
    
    print(f"Generated {len(plots)} application comparison plots:")
    for plot_name in plots:
        print(f"  - {plot_name}")


if __name__ == "__main__":
    print("StreamBazaar Demo")
    print("==================")
    
    # Run simulation
    scheduler = simulate_streaming_cluster()
    
    # Create sample visualizations
    create_sample_visualizations()
    
    # Run baseline comparison evaluation
    run_baseline_comparison_evaluation()
    
    # Run application comparison evaluation
    run_application_comparison_evaluation()
    
    # Run scalability evaluation
    print("\n--- Running Scalability Evaluation ---")
    run_scalability_evaluation()
    
    print("\nDemo completed. Check the 'output' directory for generated plots and 'evaluation_results' for CSV files and scalability plots.")