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
rt.memcpy_h2d(xs, x, 0, 0, 1, 1, M, **kw)          # only the root gets x from the host
rt.memcpy_h2d(ss, s, 0, 0, 1, R, 1, **kw)          # one scale per PE
rt.launch('go', nonblock=False)
y = np.zeros(R * M, dtype=np.float32)
rt.memcpy_d2h(y, ys, 0, 0, 1, R, M, **kw)
rt.stop()

np.testing.assert_allclose(y.reshape(R, M), np.outer(s, x), rtol=1e-6)
print(f"one send from the root reached all {R} PEs; y[row, :3] =")
print(y.reshape(R, M)[:, :3])
print("SUCCESS!")
