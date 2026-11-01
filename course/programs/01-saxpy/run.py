#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
N = int(json.load(open(f"{args.name}/out.json"))['params']['N'])

rng = np.random.default_rng(0)
x = rng.standard_normal(N).astype(np.float32)
y = rng.standard_normal(N).astype(np.float32)
a = np.float32(2.5)

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
xs, ys = rt.get_id('x'), rt.get_id('y')
rt.load(); rt.run()
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
rt.memcpy_h2d(xs, x, 0, 0, 1, 1, N, **kw)        # (x0, y0, width, height, elems per PE)
rt.memcpy_h2d(ys, y, 0, 0, 1, 1, N, **kw)
rt.launch('saxpy', a, nonblock=False)
out = np.zeros(N, dtype=np.float32)
rt.memcpy_d2h(out, ys, 0, 0, 1, 1, N, **kw)
rt.stop()

np.testing.assert_allclose(out, a * x + y, rtol=1e-6, atol=1e-6)
print("first 4:", out[:4], " expected:", (a * x + y)[:4])
print("SUCCESS!")
