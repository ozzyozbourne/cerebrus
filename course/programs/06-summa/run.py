#!/usr/bin/env cs_python
# Host side of 06-summa (adapted from Cerebras SDK 2.10.1 benchmarks/gemm-collectives_2d/run.py).
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
cfg = json.load(open(f"{args.name}/out.json"))
prm = cfg['params']
P, Mt, Kt, Nt, kern = (int(prm[k]) for k in ('P', 'Mt', 'Kt', 'Nt', 'kernel'))
M, K, N = Mt * P, Kt * P, Nt * P                    # A is M x K, B is K x N

np.random.seed(7)
A = np.random.rand(M, K).astype(np.float32)
B = np.random.rand(K, N).astype(np.float32)

# Host layout: PE (px, py) gets block row py, block column px, flattened
# column-major. reshape(rows, tile_rows, cols, tile_cols) -> (py, px, col, row).
def to_tiles(X, tr, tc):
  return X.reshape(P, tr, P, tc).transpose(0, 2, 3, 1).ravel()
def from_tiles(flat, tr, tc):
  return flat.reshape(P, P, tc, tr).transpose(0, 3, 1, 2).reshape(P * tr, P * tc)

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
rt.load(); rt.run()
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
# One memcpy per matrix covers the whole P x P rectangle: the wire order is
# row-major over PEs (py outer, px inner), Mt*Kt words per PE.
rt.memcpy_h2d(rt.get_id('A'), to_tiles(A, Mt, Kt), 0, 0, P, P, Mt * Kt, **kw)
rt.memcpy_h2d(rt.get_id('B'), to_tiles(B, Kt, Nt), 0, 0, P, P, Kt * Nt, **kw)
rt.launch('main', nonblock=False)
Cf = np.zeros(M * N, dtype=np.float32)
rt.memcpy_d2h(Cf, rt.get_id('C'), 0, 0, P, P, Mt * Nt, **kw)
S = 3 * P + 2                                         # timestamps per PE
w = np.zeros(P * P * S * 3, dtype=np.uint32)
rt.memcpy_d2h(w, rt.get_id('tsc'), 0, 0, P, P, S * 3,
              **dict(kw, data_type=MemcpyDataType.MEMCPY_16BIT))
rt.stop()

C = from_tiles(Cf, Mt, Nt)
np.testing.assert_allclose(C, A @ B, rtol=1e-5, atol=1e-6)

w = (w & 0xffff).astype(np.int64).reshape(P, P, S, 3)  # (py, px, stamp, word)
t = w[..., 0] | (w[..., 1] << 16) | (w[..., 2] << 32)
total = t[:, :, -1] - t[:, :, 0]                      # same-PE differences only
issue, cbeg, cend = t[:, :, 1:-1:3], t[:, :, 2:-1:3], t[:, :, 3:-1:3]
comp = (cend - cbeg).sum(-1)                          # compute, all steps
comm = (cbeg - issue).sum(-1)                         # issue -> both broadcasts done
py, px = P - 1, P - 1                                  # report the far corner PE
print(f"C = A·B with A {M}x{K}, B {K}x{N} on {P}x{P} PEs, tiles {Mt}x{Kt} · {Kt}x{Nt}; C[:2, :4] =")
print(np.array2string(C[:2, :4], precision=4))
print(f"kernel time (TSC, per PE, cycles): min {total.min()}, max {total.max()}")
print(f"PE ({px},{py}) over {P} steps: total {total[py, px]} = broadcast wait {comm[py, px]}"
      f" + compute {comp[py, px]} + other {total[py, px] - comm[py, px] - comp[py, px]}")
shape = f"{Kt * Nt} @fmacs of length {Mt}" if kern == 0 else f"{Kt} x (@fmuls + @fadds) of length {Mt * Nt}"
print(f"compute per step {comp[py, px] / P:.0f} cycles for {Mt * Kt * Nt} multiply-adds ({shape})")
print("SUCCESS!")
