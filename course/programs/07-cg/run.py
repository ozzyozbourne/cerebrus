#!/usr/bin/env cs_python
# Lab 5 host script: solve A x = b by CG twice on the same device, first with the host
# driving every phase, then with the device's own state machine, and check both against numpy.
# Adapted from Cerebras SDK 2.10.1 benchmarks/conjugate-gradient (run.py, device_run.py).
import argparse, json
import numpy as np
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder  # pylint: disable=no-name-in-module

p = argparse.ArgumentParser(); p.add_argument('--name'); p.add_argument('--cmaddr')
p.add_argument('--zdim', type=int, default=5); p.add_argument('--max-ite', type=int, default=30)
p.add_argument('--eps', type=float, default=1e-5)
p.add_argument('--host-ite', type=int, default=3)   # the host loop is slow to simulate; a few iterations time it
args = p.parse_args()
prm = json.load(open(f"{args.name}/out.json"))['params']
W, H, Z, ITE = int(prm['width']), int(prm['height']), args.zdim, args.max_ite
assert Z <= int(prm['MAX_ZDIM']) and ITE <= int(prm['MAX_ITE'])

# The matrix: 3-D Laplacian, 6 on the diagonal and -1 for each of the 6 neighbours,
# zero (Dirichlet) outside the H x W x Z box. Symmetric positive definite, so CG applies.
coeff = np.array([-1, -1, -1, -1, -1, -1, 6], dtype=np.float32)   # W E S N bottom top centre
def A(v):
    y = np.float32(6) * v
    for ax in range(3):
        sl = [slice(None)] * 3; sr = [slice(None)] * 3
        sl[ax] = slice(1, None); sr[ax] = slice(None, -1)
        y[tuple(sl)] -= v[tuple(sr)]; y[tuple(sr)] -= v[tuple(sl)]
    return y

b = np.random.default_rng(15).random((H, W, Z), dtype=np.float32)   # [py][px][z]
x0 = np.zeros_like(b)
tol = np.float32(args.eps * np.linalg.norm(b))

def cg_numpy(max_ite):                # the same recurrence, in f32
    x = x0.copy(); r = b - A(x); rho = np.vdot(r, r); hist = [rho]; k = 0
    while rho > tol * tol and k < max_ite:
        k += 1
        pp = r.copy() if k == 1 else r + (rho / rho_old) * pp
        w = A(pp); alpha = rho / np.vdot(pp, w)
        x = x + alpha * pp; r = r - alpha * w
        rho_old, rho = rho, np.vdot(r, r); hist.append(rho)
    return x, np.array(hist, dtype=np.float32)
HOST_ITE = min(args.host_ite, ITE)
ref = {'host': cg_numpy(HOST_ITE), 'device': cg_numpy(ITE)}

# No per-cycle trace files: this lab simulates ~10^5 cycles, which would write gigabytes of them.
rt = SdkRuntime(args.name, cmaddr=args.cmaddr, suppress_simfab_trace=True)
rt.load(); rt.run()
f32 = dict(streaming=False, order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
def h2d(sym, a, n): rt.memcpy_h2d(rt.get_id(sym), np.ascontiguousarray(a).ravel(), 0, 0, W, H, n, **f32)
def d2h(sym, n, dt=np.float32, w=None, h=None):
    out = np.zeros((h or H) * (w or W) * n, dtype=dt)
    rt.memcpy_d2h(out, rt.get_id(sym), 0, 0, w or W, h or H, n, **f32)
    return out.reshape(h or H, w or W, n)

h2d('b', b, Z); h2d('coeff', np.broadcast_to(coeff, (H, W, 7)), 7)

def collect():
    x = d2h('x', Z)
    th = d2h('t_hist', ITE + 1, np.uint32).astype(np.int64)
    return x, d2h('rho_hist', ITE + 1), th, d2h('prof', 5, np.uint32).astype(np.int64)

# ---- 1. host-driven loop: one launch per phase, and rho comes back to the host every iteration
h2d('x', x0, Z)
rt.launch('f_init', np.int16(Z), nonblock=False)
rt.launch('f_spmv_Ax', nonblock=False)
rt.launch('f_residual', nonblock=False)
rho = d2h('rho', 1, w=1, h=1)[0, 0, 0]; k = 0
while rho > tol * tol and k < HOST_ITE:
    k += 1
    for f in ('f_update_p', 'f_spmv_Ap', 'f_eta', 'f_update_x_r_rho'):
        rt.launch(f, nonblock=False)
    rho = d2h('rho', 1, w=1, h=1)[0, 0, 0]
host = collect() + (k, 'host')

# ---- 2. device-driven loop: one launch, the PEs' state machine runs every phase
h2d('x', x0, Z)
rt.launch('f_cg', np.int16(Z), np.float32(tol), np.int16(ITE), nonblock=False)
k_dev = int(np.count_nonzero(d2h('t_hist', ITE + 1, np.uint32)[0, 0]))   # iterations + 1 stamps
dev = collect() + (k_dev - 1, 'device')
rt.stop()

# ---- check and report (timings: TSC on one PE, the centre one)
py, px = H // 2, W // 2
print(f"{W} x {H} PEs x {Z} cells = {W*H*Z} unknowns; stop at |r| <= {args.eps:g} |b| or {ITE} iterations")
names = ['axpy', 'stencil SpMV', 'local dot', 'allreduce', 'control']
for label, (x, rh, th, pr, K, which) in (('host-driven loop  ', host), ('device-driven loop', dev)):
    x_ref, hist_ref = ref[which]
    assert K == len(hist_ref) - 1, f"{label}: {K} iterations, numpy needed {len(hist_ref) - 1}"
    np.testing.assert_allclose(x, x_ref, rtol=1e-4, atol=1e-5 * np.abs(x_ref).max())
    np.testing.assert_allclose(rh[py, px, :K + 1], hist_ref, rtol=1e-3, atol=1e-6 * hist_ref[0])
    assert np.all(rh[:, :, :K + 1] == rh[0, 0, :K + 1]), "every PE must see the same rho"
    if K == 0: print(f"{label}: 0 iterations"); continue
    per = (th[:, :, K] - th[:, :, 0]) / K                # durations on each PE's own clock
    split = ', '.join(f"{n} {v / K:.0f}" for n, v in zip(names, pr[py, px]) if v)
    print(f"{label}: {K} iterations, {per[py, px]:.0f} cycles/iteration on PE ({px},{py})"
          + (f"  [{split}]" if pr[py, px].any() else ""))
    if which == 'device' and pr.any():
        ar = pr[:, :, 3] / K
        print(f"  all {W*H} PEs: {per.min():.0f}-{per.max():.0f} cycles/iteration, "
              f"of which allreduce {ar.min():.0f}-{ar.max():.0f} (PE ({px},{py}) {ar[py, px]:.0f})")
K = dev[4]
rel = np.sqrt(np.maximum(dev[1][py, px, :K + 1], 0)) / np.linalg.norm(b)
print("|r_k|/|b|, k = 0..%d (device):" % K)
print(np.array2string(rel, precision=2, max_line_width=100))
true_res = np.linalg.norm(b - A(dev[0])) / np.linalg.norm(b)
print(f"true residual |b - A x|/|b| = {true_res:.2e}; max |x_wse - x_numpy| = {np.abs(dev[0] - ref['device'][0]).max():.1e}")
print("SUCCESS!")
