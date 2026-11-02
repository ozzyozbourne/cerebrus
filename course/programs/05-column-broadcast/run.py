#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
prm = json.load(open(f"{args.name}/out.json"))['params']
R, M = int(prm['R']), int(prm['M'])

x = np.linspace(-1, 1, M, dtype=np.float32)
s = np.arange(1, R + 1, dtype=np.float32)          # PE row y gets scale y+1

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
xs, ys, ss = rt.get_id('x'), rt.get_id('y'), rt.get_id('s')
rt.load(); rt.run()
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
rt.launch('start_timer', nonblock=False)          # first command: all TSCs reset together
rt.memcpy_h2d(xs, x, 0, 0, 1, 1, M, **kw)          # only the root gets x from the host
rt.memcpy_h2d(ss, s, 0, 0, 1, R, 1, **kw)          # one scale per PE
rt.launch('go', nonblock=False)
y = np.zeros(R * M, dtype=np.float32)
rt.memcpy_d2h(y, ys, 0, 0, 1, R, M, **kw)

def read_tsc(name):    # R timestamps; 16-bit words arrive in u32 slots
  w = np.zeros(3 * R, dtype=np.uint32)
  rt.memcpy_d2h(w, rt.get_id(name), 0, 0, 1, R, 3, **dict(kw, data_type=MemcpyDataType.MEMCPY_16BIT))
  w = (w & 0xffff).astype(np.int64).reshape(R, 3)
  return w[:, 0] + (w[:, 1] << 16) + (w[:, 2] << 32)
t0, t1 = read_tsc('t_start'), read_tsc('t_end')
rt.stop()

np.testing.assert_allclose(y.reshape(R, M), np.outer(s, x), rtol=1e-6)
print(f"one send from the root reached all {R} PEs; y[row, :3] =")
print(y.reshape(R, M)[:, :3])
# Each number below uses one PE's own clock only (it was reset by start_timer).
print("start_timer -> go(), per PE:", t0.tolist())
print("go() -> x sent/received, per PE:", (t1 - t0).tolist())
print("SUCCESS!")
