"""Exp C - Decoder de control C1 (fractional, no-saturante).

Re-exporta FractionalDecoder definido en el paquete (decoders/__init__.py), donde
vive junto al greedy y a C2 para compartir _greedy_core y la verificacion de
feasibility. Genotipo extendido: orden (random keys -> SPV) + intensidad alpha_g
en [0,1]; x_g = floor(alpha_g * cap_g).
"""
from collapse.decoders import FractionalDecoder

__all__ = ["FractionalDecoder"]
