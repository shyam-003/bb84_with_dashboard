## Quantum Key Distribution (QKD) Simulator

A sophisticated interactive simulator for Quantum Key Distribution protocols (**BB84** and **E91**). This tool demonstrates how the laws of quantum mechanics—specifically the *Heisenberg Uncertainty Principle* and *Quantum Entanglement*—guarantee secure communication.

**Repository:** https://github.com/shyam-003/bb84_with_dashboard

<br>

## 🚀 Key Features

 - **Interactive Dashboard :** Built with **Tkinter** and **Matplotlib** for real-time visualization of security metrics.

 - **Dual Protocols**
    - **BB84 (Prepare & Measure):** Detects eavesdroppers by monitoring the Quantum Bit Error Rate (**QBER**).  
    - **E91 (Entanglement-Based):** Verifies security by calculating the CHSH correlation value \( S \), demonstrating Bell's Inequality violation.

 - **Adversary Simulation :** Toggle an eavesdropper (**Eve**) to see how interception destroys the key or collapses entanglement.

 - **Noise Modeling :** Adjustable sliders simulate realistic fiber-optic decoherence (Depolarizing Channel).

 - **Scalable Engine :** Implements a custom **Serial Simulation** engine capable of simulating **1000+ qubits** on standard laptops without memory overflow.

<br>

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shyam-003/bb84_with_dashboard.git
cd bb84_with_dashboard
```

### 2. Install Dependencies

You need Python 3.10 or higher.
```bash
pip install qiskit qiskit-aer matplotlib numpy
```

### 3. macOS Users

If you are using Homebrew Python, you might need to install the Tkinter binding separately:
```bash
brew install python-tk@3.11
```

<br>

## 🖥️ Usage

Run the main application file to launch the dashboard:
```bash
python main.py
```

<br>

## Dashboard Controls

 1. **Protocol:** Switch between BB84 and E91.

 2. **Number of Bits:** Set the simulation size (e.g., 50 to 1000 bits/pairs). Higher numbers provide smoother statistical results.

 3. **Eve (Adversary):** Check this box to simulate a "Man-in-the-Middle" attack.

 4. **Noise Level:** Adjust the slider (0-50%) to simulate imperfect hardware.


<br>


## 🔬 Physics & Logic

<br>

**1. BB84 Protocol**

Aice sends qubits in random bases ($Z$ or $X$). Bob measures in random bases.

 - **Security Check:** They compare a subset of their keys.

 - **Threshold:** If the **QBER > 11%**, the channel is considered insecure (monitored).

 - **Simulation:** When "Eve" is enabled, she performs an Intercept-Resend attack, causing a QBER of ~25%.

<br>

**2. E91 Protocol (Ekert91)**

Alice and Bob receive entangled pairs ($|\Phi^+\rangle$). They measure in specific angles to test Bell's Inequality.

 - **Security Check:** The CHSH correlation value $S$.

 - **Classical Limit:** $S \leq 2.0$ (Insecure/Intercepted).

 - **Quantum Limit:** $S \approx 2.82$ (Secure).

 - **Simulation:** When "Eve" intercepts, she collapses the wavefunction, dropping $S$ below 2.0.

<br>

## 📂 Project Structure

```
├── main.py          # Entry point for the application
├── gui.py           # Tkinter interface and plotting logic
├── bb84.py          # BB84 protocol logic (Serial Engine)
├── e91.py           # E91 protocol logic (CHSH Test)
├── helpers.py       # Shared quantum functions & noise models
├── constants.py     # Configuration constants
└── README.md        # Documentation
```

<br>

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements (e.g., adding Privacy Amplification or Cascade Error Correction).

<br>

## 📄 License

This project is open-source and available under the MIT License.

<br>

---