# StreamBazaar

StreamBazaar is a resource-pricing and auction-based scheduler for multi-tenant streaming clusters. It implements a continuous double-auction mechanism with a dynamic pricing engine and a virtual currency system to ensure fair and efficient resource allocation.

## Project Structure

```
streambazaar/
├── config/                 # Configuration files
│   ├── hyperparameters.yaml # Hyperparameters for the system
│   ├── devices.yaml        # Device definitions and pricing
│   └── visualization.yaml  # Visualization settings
├── core/                   # Core algorithms and definitions
│   ├── __init__.py
│   ├── devices.py          # Device models and power/price calculations
│   ├── pricing.py          # Dynamic pricing engine
│   ├── auction.py          # Continuous double auction mechanism
│   ├── currency.py         # Virtual currency system
│   ├── metrics.py          # Evaluation metrics tracking
│   ├── scheduler.py         # Main scheduler implementation
│   └── baselines.py        # Baseline scheduler implementations
├── main.py                 # Main demo script
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streambazaar
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

The system is configured through YAML files in the `config/` directory:

- `hyperparameters.yaml`: System-wide hyperparameters including auction intervals, pricing parameters, and currency settings
- `devices.yaml`: Device definitions with resource specifications, base prices, and power consumption (matching the Haswell nodes from Chameleon Cloud as described in the paper)
- `visualization.yaml`: Visualization settings including color schemes, font sizes, and output formats

## Usage

Run the main demo script to see StreamBazaar in action:

```
python main.py
```

This script will:
1. Simulate a streaming cluster with multiple tenants and devices
2. Run several auction rounds with dynamic bidding
3. Generate all 20 evaluation plots mentioned in the paper and save them to the `output/` directory
4. Compare StreamBazaar with all 4 baseline schedulers mentioned in the paper:
   - Flink-Default: Native Flink scheduler with static slot allocation
   - DS2: Auto-scaling approach
   - CAPSys: Contention-aware placement strategy
   - TALOS: Task-level autoscaler
5. Evaluate all 4 streaming applications mentioned in the paper:
   - Credit Card Fraud Detection
   - Web Analytics
   - Network Intrusion Detection
   - IoT Sensor Analytics
6. Run scalability evaluation with different numbers of tenants (3, 5, 10, 20) and save results to CSV files

## Core Components

### Device Management
The `core/devices.py` module defines computing devices with their resource specifications, pricing models, and power consumption characteristics. The device configuration matches the Haswell nodes (2× Intel Xeon E5-2670 v3 with 24 cores, 128 GB DDR4 ECC memory, and 10 Gbps Ethernet) from Chameleon Cloud as described in the paper.

### Pricing Engine
The `core/pricing.py` module computes dynamic resource prices based on supply-demand dynamics using exponential smoothing with utilization-based adjustments.

### Auction Mechanism
The `core/auction.py` module implements a continuous double auction where tenants submit bids for resources and winners are determined using a greedy approximation algorithm.

### Currency System
The `core/currency.py` module manages the virtual currency system that ensures fairness and prevents resource starvation through periodic allocations and decay mechanisms.

### Metrics Tracking
The `core/metrics.py` module implements all evaluation metrics mentioned in the paper:
- Resource Utilization Efficiency (RUE)
- Tail Latency Violation Rate (TLVR)
- Economic Efficiency Index (EEI)
- Jain's Fairness Index
- Normalized Throughput
- Fairness-Performance Product (FPP)
- Migration Impact Score (MIS)

### Scheduler
The `core/scheduler.py` module integrates all components into the main StreamBazaar scheduler that orchestrates the auction process.

### Baseline Schedulers
The `core/baselines.py` module implements all 4 baseline schedulers for comparison:
- Flink-Default: Native Flink scheduler with static slot allocation
- DS2: Auto-scaling approach
- CAPSys: Contention-aware placement strategy
- TALOS: Task-level autoscaler

## Evaluation

The `evaluation/plots.py` module generates all 20 evaluation plots mentioned in the paper:

1. Resource Utilization Efficiency Comparison
2. Tail Latency Violation Rate Comparison
3. Economic Efficiency Index Comparison
4. Jain's Fairness Index Comparison
5. Normalized Throughput Comparison
6. Fairness-Performance Product Comparison
7. Migration Impact Score Comparison
8. Resource Utilization Over Time
9. Tenant Balance Distribution
10. Auction Efficiency Over Time
11. Latency Distribution by Tenant Priority
12. Resource Price Dynamics
13. Allocation Success Rate Over Time
14. Currency Consumption by Tenant
15. Backpressure Distribution
16. Operator Migration Frequency
17. Resource Utilization Heatmap
18. Auction Valuation Distribution
19. System Throughput Over Time
20. Performance vs Fairness Trade-off

Additionally, it generates application-specific comparison plots for all 4 streaming applications:
- Credit Card Fraud Detection
- Web Analytics
- Network Intrusion Detection
- IoT Sensor Analytics

Each application evaluation includes:
- Resource Efficiency Comparison
- Latency Performance Comparison
- Cost Efficiency Comparison

And an overall scheduler comparison across all applications.

## Scalability Evaluation

The `evaluation/scalability_evaluation.py` module runs experiments with different numbers of tenants (3, 5, 10, 20) for each application and saves the results in CSV format along with plots in separate folders:

- Results are saved in the `evaluation_results/` directory with separate folders for each application
- Each application folder contains CSV files for different tenant counts (3, 5, 10, 20)
- Scalability plots showing how metrics change with the number of tenants are saved in `evaluation_results/plots/`
- Each CSV file contains metrics for all schedulers at a specific tenant count for a specific application
- Metrics include Resource Utilization Efficiency, Tail Latency Violation Rate, Economic Efficiency Index, etc.

### Output Structure:
- Application-specific CSV files: `evaluation_results/{application_name}/{3,5,10,20}_tenants_results.csv`
- Scalability plots: `evaluation_results/plots/{application_name}_{metric}.png`

### Applications Evaluated:
1. Credit Card Fraud Detection
2. Web Analytics
3. Network Intrusion Detection
4. IoT Sensor Analytics

## Visualization

The `visualization/plotter.py` module provides colorblind-friendly plotting capabilities with:
- Support for line plots with different markers and line styles
- Bar plots with distinctive patterns
- Box plots with distinctive patterns
- Configurable fonts, colors, and output formats
- Automatic saving of subplots and legends separately

All plots are saved in both PNG and PDF formats in the `output/` directory, with legends saved separately as requested.

## Development

### Running Tests

To run the test suite:
```
pytest
```

### Code Structure

The code follows a modular design where each component is separated into its own module:
- Configuration is externalized to YAML files
- Algorithms are implemented in the `core/` package
- Visualization is handled by the `visualization/` package
- Evaluation plots are generated by the `evaluation/` package
- The main script demonstrates the system functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments


This implementation is based on the StreamBazaar paper by Younesi et al.
