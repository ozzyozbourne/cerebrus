#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
params = json.load(open(f"{args.name}/out.json"))['params']
N, H2D = int(params['N']), int(params['MEMCPYH2D_DATA_1_ID'])

data = np.random.default_rng(1).uniform(-10, 10, N).astype(np.float32)

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
s_sym, c_sym = rt.get_id('stats'), rt.get_id('count')
rt.load(); rt.run()
# streaming=True: pass the *color id* instead of a symbol; each element becomes a wavelet.
rt.memcpy_h2d(H2D, data, 0, 0, 1, 1, N, streaming=True,
              order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
rt.launch('wait_done', nonblock=False)   # barrier: wait until every task has run
kw = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
stats = np.zeros(4, dtype=np.float32); count = np.zeros(1, dtype=np.uint32)
rt.memcpy_d2h(stats, s_sym, 0, 0, 1, 1, 4, **kw)
rt.memcpy_d2h(count, c_sym, 0, 0, 1, 1, 1, **kw)
rt.stop()

expected = np.array([data.sum(dtype=np.float32), (data * data).sum(dtype=np.float32), data.max(), data.min()], dtype=np.float32)
print("tasks fired:", count[0], " stats:", stats, " expected:", expected)
assert count[0] == N
np.testing.assert_allclose(stats, expected, rtol=1e-4)
print("SUCCESS!")
