#!/usr/bin/env cs_python
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module
from cerebras.sdk.sdk_utils import memcpy_view, input_array_to_u32

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
args = p.parse_args()
prm = json.load(open(f"{args.name}/out.json"))['params']
N, HALF = int(prm['N']), int(prm['HALF']) != 0

rng = np.random.default_rng(0)
x = rng.standard_normal(N).astype(np.float32)
y = rng.standard_normal(N).astype(np.float32)
a = np.float32(2.5)

rt = SdkRuntime(args.name, cmaddr=args.cmaddr)
xs, ys, tss = rt.get_id('x'), rt.get_id('y'), rt.get_id('ts')
rt.load(); rt.run()
o = MemcpyOrder.ROW_MAJOR
k16 = dict(streaming=False, order=o, data_type=MemcpyDataType.MEMCPY_16BIT, nonblock=False)
k32 = dict(streaming=False, order=o, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
if HALF:   # 16-bit copy mode: one f16 in the low half of each u32 the host sends
    xh, yh = x.astype(np.float16), y.astype(np.float16)
    rt.memcpy_h2d(xs, input_array_to_u32(xh, 0, N), 0, 0, 1, 1, N, **k16)
    rt.memcpy_h2d(ys, input_array_to_u32(yh, 0, N), 0, 0, 1, 1, N, **k16)
else:
    rt.memcpy_h2d(xs, x, 0, 0, 1, 1, N, **k32)
    rt.memcpy_h2d(ys, y, 0, 0, 1, 1, N, **k32)
rt.launch('saxpy', a, nonblock=False)
if HALF:
    o32 = np.zeros(N, np.uint32); rt.memcpy_d2h(o32, ys, 0, 0, 1, 1, N, **k16)
    out = memcpy_view(o32, np.dtype(np.float16)).astype(np.float32)
    ref = np.float16(a) * xh.astype(np.float32) + yh.astype(np.float32)
    np.testing.assert_allclose(out, ref, rtol=2e-3, atol=2e-3)
else:
    out = np.zeros(N, np.float32); rt.memcpy_d2h(out, ys, 0, 0, 1, 1, N, **k32)
    np.testing.assert_allclose(out, a * x + y, rtol=1e-6, atol=1e-6)
t = np.zeros(6, np.uint32); rt.memcpy_d2h(t, tss, 0, 0, 1, 1, 6, **k16)
rt.stop()

w = memcpy_view(t, np.dtype(np.uint16)).astype(np.int64)
stamp = lambda k: w[k] | (w[k + 1] << 16) | (w[k + 2] << 32)   # 3 x u16 -> 48-bit count
print(f"N={N} {'f16 @fmach' if HALF else 'f32 @fmacs'} PAD={int(prm['PAD'])}: kernel {stamp(3) - stamp(0)} cycles (TSC)")
print("SUCCESS!")
