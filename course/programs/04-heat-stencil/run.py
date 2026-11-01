#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
p.add_argument('--steps', type=int, default=50); p.add_argument('--alpha', type=float, default=0.25)
args = p.parse_args()
prm = json.load(open(f"{args.name}/out.json"))['params']
P, n = int(prm['P']), int(prm['n'])
L = P * n

# Global rod with fixed boundary temperatures: g[0] = 1.0 (hot end), g[L+1] = 0.0
g = np.zeros(L + 2, dtype=np.float32); g[0] = 1.0
g[1 + L // 2 - 2 : 1 + L // 2 + 2] = 5.0                 # a hot spot in the middle

# Each PE gets its n cells plus the two neighbouring cells as ghosts.
local = np.stack([g[x * n : x * n + n + 2] for x in range(P)]).astype(np.float32)

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
us = rt.get_id('u')
rt.load(); rt.run()
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
rt.memcpy_h2d(us, local.ravel(), 0, 0, P, 1, n + 2, **kw)
rt.launch('run', np.uint32(args.steps), np.float32(args.alpha), nonblock=False)
res = np.zeros(P * (n + 2), dtype=np.float32)
rt.memcpy_d2h(res, us, 0, 0, P, 1, n + 2, **kw)
rt.stop()
device = res.reshape(P, n + 2)[:, 1:-1].ravel()

# Reference: identical f32 arithmetic on the host
ref = g.copy(); a = np.float32(args.alpha)
for _ in range(args.steps):
    lap = (ref[:-2] + ref[2:]) + np.float32(-2.0) * ref[1:-1]
    ref[1:-1] = ref[1:-1] + a * lap
np.testing.assert_allclose(device, ref[1:-1], rtol=1e-5, atol=1e-6)
print(f"{P} PEs x {n} cells, {args.steps} steps; temperature profile (every {max(1, L // 16)}th cell):")
print(np.array2string(device[:: max(1, L // 16)], precision=3))
print("SUCCESS!")
