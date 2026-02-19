/// QFZZ Quantum Random Number Generator
///
/// Provides quantum random number generation operations for
/// the QFZZ blockchain trust network using the Microsoft QDK.

import Std.Arrays.*;
import Std.Convert.*;

/// Generates a random integer using nBits qubits.
/// Each qubit is placed into uniform superposition via the Hadamard gate,
/// then measured to produce a truly random bit.
///
/// # Input
/// ## nBits
/// The number of random bits to generate (determines the range: 0 to 2^nBits - 1).
///
/// # Output
/// A random integer in the range [0, 2^nBits - 1].
operation GenerateRandomInt(nBits : Int) : Int {
    use qubits = Qubit[nBits];
    ApplyToEach(H, qubits);
    let results = MResetEachZ(qubits);
    ResultArrayAsInt(Reversed(results))
}
