"""
Unit tests for the Quantum Distributed Simulator project.
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.quantum_core.quantum_simulator import QuantumState, Gates, QuantumCircuit
from src.distributed_engine.distributed_simulator_engine import DistributedExecutor, Task

def test_quantum_state_initialization():
    """Tests initialization of QuantumState."""
    print("Testing QuantumState initialization...")
    state = QuantumState(3)
    assert state.num_qubits == 3
    assert state.dimension == 8
    # Check that it's initialized to |000>
    assert state.state_vector[0] == 1.0
    assert np.allclose(state.state_vector[1:], 0.0)
    print("  QuantumState initialization test passed.")

def test_quantum_state_apply_gate():
    """Tests applying single-qubit gates to QuantumState."""
    print("Testing QuantumState gate application...")
    state = QuantumState(2)
    
    # Apply Hadamard to qubit 0
    state.apply_gate(Gates.H, 0)
    
    # For |00> -> (|00> + |10>)/sqrt(2)
    expected_state = np.array([1/np.sqrt(2), 0, 1/np.sqrt(2), 0])
    assert np.allclose(state.state_vector, expected_state)
    print("  QuantumState gate application test passed.")

def test_quantum_circuit_bell_state():
    """Tests creating and simulating a Bell state circuit."""
    print("Testing Bell state circuit...")
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.measure_all()
    
    results = circuit.simulate()
    
    # Check that we have measurements for both qubits
    assert 'q0' in results['measurements']
    assert 'q1' in results['measurements']
    
    # For a Bell state, measurements should be correlated (both 0 or both 1)
    # Since this is probabilistic, we'll check that they are the same
    assert results['measurements']['q0'] == results['measurements']['q1']
    print("  Bell state circuit test passed.")

def test_distributed_executor():
    """Tests the DistributedExecutor."""
    print("Testing DistributedExecutor...")
    executor = DistributedExecutor(num_workers=2)
    
    # Define a simple circuit
    circuit_def = {"name": "Test Circuit", "num_qubits": 2, "gates": [("H", 0)]}
    
    # Submit a task
    executor.submit_task("test_task", circuit_def)
    
    # Check task status
    status = executor.get_task_status("test_task")
    assert status['id'] == "test_task"
    assert status['status'] in ["PENDING", "RUNNING", "COMPLETED"]
    
    # Wait a bit for task completion
    import time
    time.sleep(2)
    
    # Check final status
    final_status = executor.get_task_status("test_task")
    assert final_status['status'] in ["COMPLETED", "FAILED"]
    
    executor.shutdown()
    print("  DistributedExecutor test passed.")

if __name__ == '__main__':
    test_quantum_state_initialization()
    test_quantum_state_apply_gate()
    test_quantum_circuit_bell_state()
    test_distributed_executor()
    print("\nAll tests passed!")