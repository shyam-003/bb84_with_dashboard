# helpers.py
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from constants import *

def get_quantum_random_numbers(length):
    """
    Generates true random bits using a quantum circuit
    """
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    
    backend = AerSimulator()
    job = backend.run(transpile(qc, backend), shots=length, memory=True)
    return job.result().get_memory()


def get_random_bases(length):
    """
    Generates a random sequence of bases (Z or X).
    """
    random_bits = get_quantum_random_numbers(length)
    return [BASIS_Z if b == '0' else BASIS_X for b in random_bits]


def prepare_alice_states(circuit, bits, bases):
    """
    Encodes Alice's bits into the quantum circuit.
    """
    for i in range(len(bits)):
        if bases[i] == BASIS_Z:
            if bits[i] == BIT_1:
                circuit.x(i)
            
        elif bases[i] == BASIS_X:
            if bits[i] == BIT_0:
                circuit.h(i)
            else:
                circuit.x(i)
                circuit.h(i)
    circuit.barrier()


def simulate_eve(circuit, length):
    """
    Simulates Eve intercepting the qubits.
    She chooses random bases, measures, and resends.
    """
    eve_bases = get_random_bases(length)
    for i in range(length):
        if eve_bases[i] == BASIS_X:
            circuit.h(i)
        
        circuit.measure(i, i)
        
        if eve_bases[i] == BASIS_X:
            circuit.h(i)
            
    circuit.barrier()
    return eve_bases


def measure_bob(circuit, bases):
    """
    Bob measures the incoming qubits.
    """
    for i in range(len(bases)):
        if bases[i] == BASIS_X:
            circuit.h(i)
        circuit.measure(i, i)

def get_noise_model(error_rate):
    """
    Creates a noise model for the simulator.
    error_rate: 0.0 to 1.0 (0% to 100%)
    """
    noise_model = NoiseModel()
    if error_rate > 0:
        # Add depolarizing error (bit flip + phase flip)
        error = depolarizing_error(error_rate, 1)
        noise_model.add_all_qubit_quantum_error(error, ['x', 'h', 'id'])
    return noise_model

