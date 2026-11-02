#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
prm = json.load(open(f"{args.name}/out.json"))['params']
P, M = int(prm['P']), int(prm['M'])

V = np.random.default_rng(2).standard_normal((P, M)).astype(np.float32)   # row x = PE x
rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
vs = rt.get_id('v')
rt.load(); rt.run()
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
rt.memcpy_h2d(vs, V.ravel(), 0, 0, P, 1, M, **kw)   # PE x receives V[x, :]
rt.launch('start_timer', nonblock=False)           # every PE: reset its TSC
rt.launch('reduce', nonblock=False)                # every PE: start its one DSD op
out = np.zeros(M, dtype=np.float32)
rt.memcpy_d2h(out, vs, P - 1, 0, 1, 1, M, **kw)    # result lives on the last PE

def read_tsc(name):    # P timestamps; 16-bit words arrive in u32 slots
  w = np.zeros(3 * P, dtype=np.uint32)
  rt.memcpy_d2h(w, rt.get_id(name), 0, 0, P, 1, 3, **dict(kw, data_type=MemcpyDataType.MEMCPY_16BIT))
  w = (w & 0xffff).astype(np.int64).reshape(P, 3)
  return w[:, 0] + (w[:, 1] << 16) + (w[:, 2] << 32)
t0, t1 = read_tsc('t_start'), read_tsc('t_end')
rt.stop()

np.testing.assert_allclose(out, V.sum(axis=0), rtol=1e-5, atol=1e-5)
print(f"summed {P} vectors of length {M} across the row; first 4:", out[:4])
# Both stamps of a pair come from the SAME PE's clock; never subtract across PEs.
print("reduce() start -> op done, per PE (own TSC):", (t1 - t0).tolist())
print(f"kernel on the last PE: {t1[-1] - t0[-1]} cycles (host I/O excluded)")
print("SUCCESS!")
