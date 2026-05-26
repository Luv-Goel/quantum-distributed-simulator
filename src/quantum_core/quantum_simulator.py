"""
Quantum Core Module for Quantum Distributed Simulator

This module provides the fundamental building blocks for quantum circuit simulation, including:
- Quantum state representation
- Basic quantum gates (Hadamard, CNOT, Pauli-X, Y, Z)
- Measurement operations
- Circuit construction utilities
"""

import numpy as np
from scipy.linalg import expm

class QuantumState:
    """
    Represents a quantum state using a state vector.
    """
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.dimension = 2**num_qubits
        self.state_vector = np.zeros(self.dimension, dtype=complex)
        self.state_vector[0] = 1.0 # Initialize to |0...0>

    def __str__(self):
        return f"QuantumState(num_qubits={self.num_qubits}, vector={self.state_vector})"

    def apply_gate(self, gate_matrix: np.ndarray, target_qubit: int):
        """
        Applies a single-qubit gate to a specific target qubit.
        """
        if not (0 <= target_qubit < self.num_qubits):
            raise ValueError("Target qubit out of range.")
        if gate_matrix.shape != (2, 2):
            raise ValueError("Gate matrix must be 2x2 for a single qubit.")

        # Construct the full (tensor product) operator for the entire system
        identity = np.eye(2)
        full_gate = 1
        for i in range(self.num_qubits):
            if i == target_qubit:
                full_gate = np.kron(full_gate, gate_matrix)
            else:
                full_gate = np.kron(full_gate, identity)

        self.state_vector = full_gate @ self.state_vector
        # Normalize after gate application (for numerical stability, if needed)
        self.state_vector /= np.linalg.norm(self.state_vector)

    def measure(self, qubit_index: int) -> int:
        """
        Performs a measurement on a specific qubit and collapses the state.
        Returns 0 or 1.
        """
        if not (0 <= qubit_index < self.num_qubits):
            raise ValueError("Qubit index out of range.")
        
        # Calculate probabilities for outcomes (0 and 1) for the target qubit
        prob_0 = 0
        prob_1 = 0
        
        # Iterate through state vector elements
        for i in range(self.dimension):
            # Check the bit at qubit_index (from right, 0-indexed)
            if (i >> qubit_index) & 1 == 0: # If the qubit is 0
                prob_0 += np.abs(self.state_vector[i])**2
            else: # If the qubit is 1
                prob_1 += np.abs(self.state_vector[i])**2

        # Normalize probabilities (due to floating point inaccuracies)
        total_prob = prob_0 + prob_1
        prob_0 /= total_prob
        prob_1 /= total_prob
        
        # Randomly select outcome based on probabilities
        outcome = np.random.choice([0, 1], p=[prob_0, prob_1])

        # Collapse the state vector
        if outcome == 0:
            # Zero out amplitudes where qubit is 1
            for i in range(self.dimension):
                if (i >> qubit_index) & 1 == 1:
                    self.state_vector[i] = 0
        else:
            # Zero out amplitudes where qubit is 0
            for i in range(self.dimension):
                if (i >> qubit_index) & 1 == 0:
                    self.state_vector[i] = 0
        
        # Renormalize the state vector after collapse
        self.state_vector /= np.linalg.norm(self.state_vector)
        
        return outcome

class Gates:
    """
    Collection of common quantum gates.
    """
    H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
    X = np.array([[0, 1], [1, 0]]) # Pauli-X (NOT gate)
    Y = np.array([[0, -1j], [1j, 0]]) # Pauli-Y
    Z = np.array([[1, 0], [0, -1]]) # Pauli-Z
    # Add more gates as needed

    @staticmethod
    def CNOT(control_qubit: int, target_qubit: int, num_qubits: int) -> np.ndarray:
        """
        Constructs a CNOT gate for a system of num_qubits.
        """
        if not (0 <= control_qubit < num_qubits and 0 <= target_qubit < num_qubits and control_qubit != target_qubit):
            raise ValueError("Invalid control/target qubits or num_qubits.")
        
        cnot_gate = np.eye(2**num_qubits, dtype=complex)
        for i in range(2**num_qubits):
            # Check if control qubit is 1
            if (i >> control_qubit) & 1 == 1:
                # Flip target qubit bit
                j = i ^ (1 << target_qubit) # XOR with (1 << target_qubit) flips the bit
                cnot_gate[i, i] = 0 # Original state maps to 0
                cnot_gate[i, j] = 1 # Map to flipped state
            else:
                cnot_gate[i, i] = 1 # If control is 0, nothing changes
        return cnot_gate

class QuantumCircuit:
    """
    Represents a quantum circuit as a sequence of operations.
    """
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.operations = [] # List of (gate_type, target_qubit, control_qubit_if_any)

    def h(self, target_qubit: int):
        self.operations.append(('H', target_qubit))

    def x(self, target_qubit: int):
        self.operations.append(('X', target_qubit))

    def cnot(self, control_qubit: int, target_qubit: int):
        self.operations.append(('CNOT', target_qubit, control_qubit))

    def measure_all(self):
        for i in range(self.num_qubits):
            self.operations.append(('MEASURE', i))

    def simulate(self) -> Dict[str, Any]:
        """
        Simulates the quantum circuit and returns measurement results.
        """
        state = QuantumState(self.num_qubits)
        results = {}

        for op_idx, op in enumerate(self.operations):
            op_type = op[0]

            if op_type == 'H':
                target_qubit = op[1]
                state.apply_gate(Gates.H, target_qubit)
            elif op_type == 'X':
                target_qubit = op[1]
                state.apply_gate(Gates.X, target_qubit)
            elif op_type == 'CNOT':
                target_qubit = op[1]
                control_qubit = op[2]
                # CNOT is a multi-qubit gate, needs direct application to state vector
                full_cnot_gate = Gates.CNOT(control_qubit, target_qubit, self.num_qubits)
                state.state_vector = full_cnot_gate @ state.state_vector
            elif op_type == 'MEASURE':
                qubit_index = op[1]
                measurement = state.measure(qubit_index)
                results[f'q{qubit_index}'] = measurement
            else:
                raise ValueError(f"Unknown operation type: {op_type}")
        
        return {"final_state": state.state_vector, "measurements": results}


if __name__ == "__main__":
    # Example: Bell State Circuit (Entanglement)
    num_qubits_bell = 2
    bell_circuit = QuantumCircuit(num_qubits_bell)
    bell_circuit.h(0) # Apply Hadamard to qubit 0
    bell_circuit.cnot(0, 1) # Apply CNOT with qubit 0 as control, qubit 1 as target
    bell_circuit.measure_all()

    print("\n--- Simulating Bell State ---")
    bell_results = bell_circuit.simulate()
    print("Final State:", bell_results['final_state'])
    print("Measurements:", bell_results['measurements'])
    
    # Example: Simple X gate on 1 qubit
    num_qubits_x = 1
    x_circuit = QuantumCircuit(num_qubits_x)
    x_circuit.x(0)
    x_circuit.measure_all()
    
    print("\n--- Simulating X Gate ---")
    x_results = x_circuit.simulate()
    print("Final State:", x_results['final_state'])
    print("Measurements:", x_results['measurements'])

