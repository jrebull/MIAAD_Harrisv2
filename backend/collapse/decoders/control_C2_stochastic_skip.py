"""Exp C - Decoder de control C2 (stochastic-skip, intermedio).

Re-exporta StochasticSkipDecoder definido en el paquete (decoders/__init__.py).
Greedy con probabilidad de SALTAR un grupo (dejarlo en 0) gobernada por una key
adicional: skip si key < 0.5. Mas suave que C1.
"""
from collapse.decoders import StochasticSkipDecoder

__all__ = ["StochasticSkipDecoder"]
