# meshes/

Mesh-generation pipeline for the M2-M5 mesh family used throughout the dissertation. The four meshes share the same topological layout and 2D leading-edge / trailing-edge resolution, differing only in the chordwise and wall-normal refinement that scales the total element count.

## Files

- `generate_naca0012_mesh.py` - parametric mesh-generation script using the Gmsh Python API. Builds a 2D NACA 0012 base mesh with boundary-layer and wake refinement fields, then extrudes spanwise to a fully hexahedral 3D mesh with periodic z-faces.
- `build_all_meshes.sh` - driver script that runs `generate_naca0012_mesh.py` four times with the calibrated parameters for M2-M5, then converts each `.msh` to Nek `.re2` via `gmsh2nek`.

## Mesh family

| Mesh | Elements | DOF at N=7 ($\times 10^6$) | Used for |
|---|---|---|---|
| M1 | 2,562 | 1.30 | Excluded (globally invalid spanwise extrusion at nz=2) |
| M2 | 5,076 | 2.60 | GPU weak scaling, baseline |
| M3 | 10,504 | 5.38 | CPU/GPU weak scaling |
| M4 | 20,060 | 10.27 | Validation, strong scaling, production |
| M5 | 40,396 | 20.68 | CPU weak scaling, largest point |

All four production meshes use 4 spanwise layers over an `L_z = 0.2c` extent.

## Calibrated parameters

These are the exact values that produced the element counts reported in the dissertation. They were established through bisection search on the 2D quad count and confirmed by running each generation end-to-end:

```bash
# M2 (~5,076 hex)
python3 generate_naca0012_mesh.py \
    --lc-wall 0.04  --lc-far 2.0  --lc-wake 0.2  \
    --nz 4 -o naca0012_M2.msh

# M3 (~10,504 hex)
python3 generate_naca0012_mesh.py \
    --lc-wall 0.028 --lc-far 1.4  --lc-wake 0.14 \
    --nz 4 -o naca0012_M3.msh

# M4 (~20,060 hex)
python3 generate_naca0012_mesh.py \
    --lc-wall 0.02  --lc-far 1.1  --lc-wake 0.1  \
    --nz 4 -o naca0012_M4.msh

# M5 (~40,396 hex)
python3 generate_naca0012_mesh.py \
    --lc-wall 0.013 --lc-far 0.8  --lc-wake 0.07 \
    --nz 4 -o naca0012_M5.msh
```

Or run all four at once via the driver:

```bash
./build_all_meshes.sh
```

## Geometry

- NACA 0012 aerofoil, chord `c = 1`, angle of attack 0°
- Closed trailing edge using modified coefficient `a4 = -0.1036` (standard NACA closed-TE convention)
- Cosine-spaced surface points (200 per half-surface by default)
- Domain `[-5c, 16c] x [-5c, 5c] x [0, 0.2c]`
- Periodic spanwise boundaries

## Refinement fields

The script uses three Gmsh mesh-size fields combined by a `Min` field:

1. **Distance + Threshold** from the aerofoil surface (boundary-layer style). `SizeMin = lc_wall` at the wall, transitioning smoothly to `SizeMax = lc_far` at distance 3c.
2. **Box** refinement in the wake region `[1, 12] x [-1.5, 1.5]` with `lc_wake` inside and `lc_far` outside.

This is what produces the visible boundary-layer clustering around the aerofoil and the dense wake region downstream of the trailing edge.

## Conversion to Nek format

After running the Python script you have `naca0012_M{2,3,4,5}.msh`. The `gmsh2nek` tool from the Nek5000 distribution converts these to the binary `.re2` format that both Nek5000 and NekRS read natively. The driver script `build_all_meshes.sh` automates this with the correct interactive prompts:

- Mesh dimension: `3`
- Solid mesh: `0` (no)
- Periodic surface pairs: `1`
- Periodic surface IDs: `5 6` (the two z-faces from the physical-group convention below)

The conversion produces a `naca0012_M*.re2` file ready to drop into any of the case directories under `cases/`.

## Curve stripping (important for SEM stability)

The `gmsh2nek` conversion produces curved-element representations of the aerofoil surface that trigger negative Jacobians at the trailing edge under high-order curvature projection (Section 3.3 of the dissertation). Both the validation and scaling user routines (`naca0012.usr`) include a curve-stripping step in `usrdat()` that replaces every curved face with its straight-sided equivalent at vertex-correct positions. Do **not** remove the curve-stripping code from the user routines.

## Boundary identifier convention

The Gmsh physical-surface tags are written into the converted mesh as integer boundary identifiers. After the down-shift applied in `usrdat()`:

| Identifier (in `.usr`) | Gmsh physical tag | Boundary |
|---|---|---|
| 1 | 2 | Aerofoil surface (no-slip wall, mapped to `W ` in `usrdat2`) |
| 2 | 3 | Inflow (Dirichlet velocity, mapped to `v `) |
| 3 | 4 | Outflow (natural outflow, mapped to `O `) |
| 4 | 5, 6 | Spanwise periodic faces (mapped to `SYM`) |

If you alter the physical-group ordering inside `generate_naca0012_mesh.py`, adjust the conditional logic in `usrdat()` and `usrdat2()` of the case `naca0012.usr` files accordingly.

## Dependencies

```bash
pip install gmsh numpy
```

On macOS, `brew install gmsh` additionally provides the standalone GMSH GUI binary for visual inspection of the generated meshes. On Linux, the `gmsh` package via apt/yum supplies the same.
