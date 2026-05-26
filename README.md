# Quantum Distributed Simulator

A distributed simulator for quantum computing models with support for cloud-based parallel execution.

## Overview

This project aims to build a scalable and efficient simulator for quantum circuits and algorithms, leveraging distributed computing techniques to handle larger quantum systems and complex simulations that exceed the capabilities of single-node machines.

## Features

- Quantum circuit simulation core with accurate gate implementations
- Distributed execution engine for parallel simulations
- Support for various quantum gates and measurements
- Scalable architecture for large quantum states
- Cloud deployment readiness
- Comprehensive test suite

## Installation

```bash
git clone https://github.com/Luv-Goel/quantum-distributed-simulator
cd quantum-distributed-simulator
pip install -r requirements.txt
```

## Usage

### Basic Quantum Circuit Simulation

```python
import numpy as np
from src.quantum_core.quantum_simulator import QuantumCircuit, Gates

# Create a Bell state circuit
num_qubits = 2
circuit = QuantumCircuit(num_qubits)

# Apply Hadamard to qubit 0
circuit.h(0)
# Apply CNOT with qubit 0 as control, qubit 1 as target
circuit.cnot(0, 1)

# Measure both qubits
circuit.measure_all()

# Simulate the circuit
results = circuit.simulate()
print("Final state:", results['final_state'])
print("Measurements:", results['measurements'])
```

### Multi-Qubit Operations

```python
from src.quantum_core.quantum_simulator import QuantumCircuit

# Create a 3-qubit GHZ state circuit
circuit = QuantumCircuit(3)

# Create GHZ state: |000> + |111>
circuit.h(0)           # Apply Hadamard to qubit 0
circuit.cnot(0, 1)     # CNOT: control 0, target 1
circuit.cnot(0, 2)     # CNOT: control 0, target 2
circuit.measure_all()

results = circuit.simulate()
print("GHZ state measurements:", results['measurements'])
```

### Using the Distributed Execution Engine

```python
from src.distributed_engine.distributed_simulator_engine import DistributedExecutor
import time

# Create distributed executor
executor = DistributedExecutor(num_workers=4)

# Define quantum circuits to simulate
circuits = [
    {"id": "bell_state", "definition": {"num_qubits": 2, "gates": [("H", 0), ("CNOT", 0, 1)]}},
    {"id": "ghz_state", "definition": {"num_qubits": 3, "gates": [("H", 0), ("CNOT", 0, 1), ("CNOT", 0, 2)]}},
    {"id": "random_circuit", "definition": {"num_qubits": 4, "gates": [("H", 0), ("H", 1), ("CNOT", 0, 2), ("X", 3)]}}
]

# Submit tasks for distributed execution
for circuit_info in circuits:
    executor.submit_task(circuit_info["id"], circuit_info["definition"])

# Monitor execution (in a real application, you'd use callbacks or async patterns)
time.sleep(5)  # Wait for tasks to complete

# Check results
for circuit_info in circuits:
    status = executor.get_task_status(circuit_info["id"])
    print(f"Circuit {circuit_info['id']}: {status['status']}")
    if status['status'] == 'COMPLETED':
        print(f"  Result: {status['result']}")

executor.shutdown()
```

## Running Tests

To run the test suite:

```bash
python -m pytest tests/ -v
```

## Project Structure

```
quantum-distributed-simulator/
├── src/
│   ├── quantum_core/           # Core quantum simulation components
│   │   ├── quantum_simulator.py
│   │   └── ...
│   ├── distributed_engine/     # Distributed execution components
│   │   └── distributed_simulator_engine.py
│   ├── utils/                  # Utility functions
│   └── ...
├── tests/                      # Unit and integration tests
├── docs/                       # Documentation
│   └── architecture/
├── examples/                   # Example notebooks and scripts
├── requirements.txt            # Project dependencies
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.