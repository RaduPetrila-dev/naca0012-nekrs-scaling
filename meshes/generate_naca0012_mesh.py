#!/usr/bin/env python3
"""
Generate 3D NACA 0012 all-hex mesh for NekRS / Nek5000 spectral element solvers.

Requirements:
    pip install gmsh numpy

Final calibrated mesh family used in the dissertation (all 4 spanwise layers,
producing pure-hex meshes after extrusion + recombination):

    M2 (~ 5,076  hex):  --lc-wall 0.04   --lc-far 2.0  --lc-wake 0.2   --nz 4
    M3 (~10,504  hex):  --lc-wall 0.028  --lc-far 1.4  --lc-wake 0.14  --nz 4
    M4 (~20,060  hex):  --lc-wall 0.02   --lc-far 1.1  --lc-wake 0.1   --nz 4
    M5 (~40,396  hex):  --lc-wall 0.013  --lc-far 0.8  --lc-wake 0.07  --nz 4

    (M1 with --lc-wall 0.05 --lc-far 2.5 --lc-wake 0.25 --nz 2 produces
    ~2,562 hex but was excluded from the final mesh family because its
    spanwise extrusion proved globally invalid; see Section 3.3 of the
    dissertation.)

Usage:
    # Test 2D first (fast, lets you check element count before extrusion):
    python3 generate_naca0012_mesh.py --lc-wall 0.02 --lc-far 1.1 --lc-wake 0.1 \\
                                      --mesh-2d --gui -o test_2d.msh

    # Generate full 3D M4 mesh:
    python3 generate_naca0012_mesh.py --lc-wall 0.02 --lc-far 1.1 --lc-wake 0.1 \\
                                      --nz 4 -o naca0012_M4.msh

    # Open result in GMSH GUI for visual inspection:
    python3 generate_naca0012_mesh.py --lc-wall 0.02 --lc-far 1.1 --lc-wake 0.1 \\
                                      --nz 4 -o naca0012_M4.msh --gui

Domain: [-5c, 16c] x [-5c, 5c] x [0, 0.2c]
Aerofoil: NACA 0012, chord c=1, AoA=0, closed trailing edge (a4=-0.1036).
BCs: wall (aerofoil), inflow (left+top+bottom far-field), outflow (right),
periodic (spanwise z-faces).
"""

import gmsh
import numpy as np
import argparse
import sys


def naca0012_halfthickness(x):
    """
    NACA 0012 half-thickness at normalised x-coordinate.
    Uses modified coefficient a4=-0.1036 to give a closed trailing edge.
    At x=0 (LE) and x=1 (TE), thickness is exactly zero.
    """
    a4 = -0.1036  # closed TE
    return 0.6 * (
        0.2969 * np.sqrt(np.maximum(x, 0.0))
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        + a4 * x**4
    )


def create_mesh(args):
    gmsh.initialize()
    if not args.gui:
        gmsh.option.setNumber("General.Verbosity", 3)
    gmsh.model.add("naca0012")
    geo = gmsh.model.geo

    # ================================================================
    # 1. AEROFOIL GEOMETRY
    # ================================================================
    n = args.n_pts
    beta = np.linspace(0, np.pi, n)
    xc = 0.5 * (1.0 - np.cos(beta))           # cosine spacing on [0, 1]
    yt = naca0012_halfthickness(xc)

    # Build closed contour: TE -> upper surface -> LE -> lower surface -> TE
    # Going clockwise when viewed from +z (required for inner hole loop).
    foil_pt_tags = []

    # Trailing edge at (1, 0)
    te_tag = geo.addPoint(1.0, 0.0, 0.0, args.lc_wall)
    foil_pt_tags.append(te_tag)

    # Upper surface: near-TE down to near-LE (indices n-2 down to 1)
    for i in range(n - 2, 0, -1):
        tag = geo.addPoint(float(xc[i]), float(yt[i]), 0.0, args.lc_wall)
        foil_pt_tags.append(tag)

    # Leading edge at (0, 0)
    le_tag = geo.addPoint(0.0, 0.0, 0.0, args.lc_wall)
    foil_pt_tags.append(le_tag)

    # Lower surface: near-LE back up to near-TE (indices 1 up to n-2)
    for i in range(1, n - 1):
        tag = geo.addPoint(float(xc[i]), float(-yt[i]), 0.0, args.lc_wall)
        foil_pt_tags.append(tag)

    # Closed spline: last point reconnects to the first (TE)
    foil_spline = geo.addSpline(foil_pt_tags + [te_tag])
    foil_loop = geo.addCurveLoop([foil_spline])

    print(f"Aerofoil: {len(foil_pt_tags)} points, spline tag={foil_spline}")

    # ================================================================
    # 2. FAR-FIELD RECTANGLE
    # ================================================================
    x_in = args.x_in
    x_out = args.x_out
    y_top = args.y_extent
    y_bot = -args.y_extent

    p_bl = geo.addPoint(x_in,  y_bot, 0.0, args.lc_far)
    p_br = geo.addPoint(x_out, y_bot, 0.0, args.lc_far)
    p_tr = geo.addPoint(x_out, y_top, 0.0, args.lc_far)
    p_tl = geo.addPoint(x_in,  y_top, 0.0, args.lc_far)

    # Rectangle lines (counter-clockwise = outer boundary convention)
    l_bottom = geo.addLine(p_bl, p_br)   # bottom far-field
    l_right  = geo.addLine(p_br, p_tr)   # outlet (x = x_out)
    l_top    = geo.addLine(p_tr, p_tl)   # top far-field
    l_left   = geo.addLine(p_tl, p_bl)   # inlet (x = x_in)

    rect_loop = geo.addCurveLoop([l_bottom, l_right, l_top, l_left])

    # ================================================================
    # 3. FLOW DOMAIN = RECTANGLE WITH AEROFOIL HOLE
    # ================================================================
    flow_surf = geo.addPlaneSurface([rect_loop, foil_loop])
    geo.synchronize()

    print(f"Flow surface tag: {flow_surf}")
    print(f"Rectangle lines: bottom={l_bottom}, right={l_right}, "
          f"top={l_top}, left={l_left}")

    # ================================================================
    # 4. MESH SIZE FIELDS
    # ================================================================
    # Field 1: distance from aerofoil surface
    gmsh.model.mesh.field.add("Distance", 1)
    gmsh.model.mesh.field.setNumbers(1, "CurvesList", [foil_spline])
    gmsh.model.mesh.field.setNumber(1, "Sampling", 1000)

    # Field 2: boundary-layer-style refinement (smooth transition)
    gmsh.model.mesh.field.add("Threshold", 2)
    gmsh.model.mesh.field.setNumber(2, "InField", 1)
    gmsh.model.mesh.field.setNumber(2, "SizeMin", args.lc_wall)
    gmsh.model.mesh.field.setNumber(2, "SizeMax", args.lc_far)
    gmsh.model.mesh.field.setNumber(2, "DistMin", 0.005)    # BL inner edge
    gmsh.model.mesh.field.setNumber(2, "DistMax", 3.0)      # BL outer edge

    # Field 3: wake refinement box downstream of the trailing edge
    gmsh.model.mesh.field.add("Box", 3)
    gmsh.model.mesh.field.setNumber(3, "VIn",  args.lc_wake)
    gmsh.model.mesh.field.setNumber(3, "VOut", args.lc_far)
    gmsh.model.mesh.field.setNumber(3, "XMin",  1.0)
    gmsh.model.mesh.field.setNumber(3, "XMax", 12.0)
    gmsh.model.mesh.field.setNumber(3, "YMin", -1.5)
    gmsh.model.mesh.field.setNumber(3, "YMax",  1.5)
    gmsh.model.mesh.field.setNumber(3, "Thickness", 1.5)

    # Field 4: take the minimum of the two refinement fields
    gmsh.model.mesh.field.add("Min", 4)
    gmsh.model.mesh.field.setNumbers(4, "FieldsList", [2, 3])
    gmsh.model.mesh.field.setAsBackgroundMesh(4)

    # Disable default size sources so only our explicit fields are used
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints",        0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature",     0)

    # ================================================================
    # 5. MESHING OPTIONS (target: 100 % quads)
    # ================================================================
    # Algorithm 11 (Quasi-Structured Quad) is the cleanest way to
    # produce a pure-quad 2D mesh from this geometry. Combined with
    # RecombineAll = 1 and Recombine3DAll = 1, the spanwise extrusion
    # in section 7 then yields a fully hexahedral 3D mesh.
    gmsh.option.setNumber("Mesh.Algorithm",        11)
    gmsh.option.setNumber("Mesh.RecombineAll",      1)
    gmsh.option.setNumber("Mesh.Recombine3DAll",    1)

    if args.subdivide:
        # Fallback for stubborn cases: subdivide leftover tris into quads.
        # This roughly triples the count in the affected region.
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)

    # ================================================================
    # 6. 2D-ONLY MODE (for fast element-count testing)
    # ================================================================
    if args.mesh_2d:
        gmsh.model.mesh.generate(2)

        # Count 2D elements by type
        types_2d, tags_2d, _ = gmsh.model.mesh.getElements(2)
        n_quads = 0
        n_tris  = 0
        for etype, etags in zip(types_2d, tags_2d):
            name = gmsh.model.mesh.getElementProperties(etype)[0]
            count = len(etags)
            if "Triangle" in name:
                n_tris  += count
            else:
                n_quads += count

        print(f"\n{'='*50}")
        print(f"  2D MESH STATISTICS")
        print(f"{'='*50}")
        print(f"  Quadrilaterals: {n_quads}")
        print(f"  Triangles:      {n_tris}")
        if n_tris > 0:
            pct = 100.0 * n_tris / (n_quads + n_tris)
            print(f"  WARNING: {pct:.1f}% triangles. "
                  f"Run with --subdivide to force all-quad.")
        print(f"  Projected 3D hexes (x{args.nz} layers): "
              f"{n_quads * args.nz}")
        print(f"{'='*50}\n")

        gmsh.option.setNumber("Mesh.ElementOrder", args.order)
        gmsh.model.mesh.setOrder(args.order)
        gmsh.write(args.output)
        print(f"2D mesh saved to: {args.output}")
        print(f"Visualise:        gmsh {args.output}")

        if args.gui:
            gmsh.fltk.run()
        gmsh.finalize()
        return

    # ================================================================
    # 7. 3D EXTRUSION (structured layers in z-direction)
    # ================================================================
    print(f"\nExtruding flow surface {args.nz} layers in z over "
          f"{args.z_span}c ...")

    out = geo.extrude(
        [(2, flow_surf)],
        0, 0, args.z_span,
        numElements=[args.nz],
        recombine=True
    )
    geo.synchronize()

    # Parse extrusion output. The order returned by geo.extrude is:
    #   [top_face, volume,
    #    lateral_from_l_bottom,
    #    lateral_from_l_right,
    #    lateral_from_l_top,
    #    lateral_from_l_left,
    #    lateral_from_foil_spline]
    top_face   = out[0][1]
    volume     = out[1][1]
    lat_bottom = out[2][1]    # y = -5  far-field
    lat_right  = out[3][1]    # x = 16  outlet
    lat_top    = out[4][1]    # y = +5  far-field
    lat_left   = out[5][1]    # x = -5  inlet
    lat_wall   = out[6][1]    # aerofoil surface

    print(f"Extruded entities:")
    print(f"  Volume:     {volume}")
    print(f"  Top face:   {top_face}")
    print(f"  Wall:       {lat_wall}")
    print(f"  Inlet:      {lat_left}")
    print(f"  Outlet:     {lat_right}")
    print(f"  Top ff:     {lat_top}")
    print(f"  Bottom ff:  {lat_bottom}")

    # Verify by bounding box (safety check against extrusion-order changes)
    def bbox_str(dim, tag):
        bb = gmsh.model.getBoundingBox(dim, tag)
        return (f"x=[{bb[0]:.2f},{bb[3]:.2f}] "
                f"y=[{bb[1]:.2f},{bb[4]:.2f}] "
                f"z=[{bb[2]:.2f},{bb[5]:.2f}]")

    print(f"\nBounding box verification:")
    print(f"  Wall:   {bbox_str(2, lat_wall)}")
    print(f"  Inlet:  {bbox_str(2, lat_left)}")
    print(f"  Outlet: {bbox_str(2, lat_right)}")

    # ================================================================
    # 8. PHYSICAL GROUPS (boundary conditions for NekRS / Nek5000)
    # ================================================================
    # Tag numbering matches the SEM BC convention used downstream:
    #   1 = fluid volume
    #   2 = wall (no-slip)
    #   3 = inflow (velocity Dirichlet)
    #   4 = outflow (zero-gradient)
    #   5 = periodic z=0
    #   6 = periodic z=Lz
    gmsh.model.addPhysicalGroup(3, [volume],    tag=1, name="fluid")
    gmsh.model.addPhysicalGroup(2, [lat_wall],  tag=2, name="wall")
    gmsh.model.addPhysicalGroup(2, [lat_left, lat_top, lat_bottom],
                                                tag=3, name="inflow")
    gmsh.model.addPhysicalGroup(2, [lat_right], tag=4, name="outflow")
    gmsh.model.addPhysicalGroup(2, [flow_surf], tag=5, name="periodicZ0")
    gmsh.model.addPhysicalGroup(2, [top_face],  tag=6, name="periodicZ1")

    # ================================================================
    # 9. PERIODIC SURFACE MAPPING (z-faces)
    # ================================================================
    # 4x4 affine matrix, row-major, translating by z_span in z.
    translation = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, args.z_span,
        0, 0, 0, 1
    ]
    gmsh.model.mesh.setPeriodic(2, [top_face], [flow_surf], translation)

    # ================================================================
    # 10. GENERATE 3D MESH
    # ================================================================
    print("\nGenerating 3D mesh ...")
    gmsh.model.mesh.generate(3)

    # Set element order (order 2 for SEM compatibility)
    gmsh.option.setNumber("Mesh.ElementOrder", args.order)
    gmsh.model.mesh.setOrder(args.order)

    # ================================================================
    # 11. MESH STATISTICS
    # ================================================================
    types_3d, tags_3d, _ = gmsh.model.mesh.getElements(3)
    total_3d  = 0
    hex_count = 0
    all_hex   = True

    print(f"\n{'='*50}")
    print(f"  3D MESH STATISTICS")
    print(f"{'='*50}")

    for etype, etags in zip(types_3d, tags_3d):
        name  = gmsh.model.mesh.getElementProperties(etype)[0]
        count = len(etags)
        total_3d += count
        print(f"  {name}: {count}")
        if "Hex" in name:
            hex_count += count
        else:
            all_hex = False

    print(f"  --------------------------------")
    print(f"  Total 3D elements: {total_3d}")
    print(f"  All hexahedral:    {all_hex}")

    if not all_hex:
        print(f"\n  WARNING: {total_3d - hex_count} non-hex elements found.")
        print(f"  SEM solvers require all-hex meshes.")
        print(f"  Try running with --subdivide flag.")

    # Target check
    print(f"\n  Mesh family targets (calibrated for nz=4):")
    print(f"    M2 = 5,076 hex    M3 = 10,504 hex")
    print(f"    M4 = 20,060 hex   M5 = 40,396 hex")
    print(f"  Your mesh: {total_3d} hex elements")

    # Degrees of freedom at the dissertation's polynomial order (N=7)
    dof = total_3d * (7 + 1)**3
    print(f"  Degrees of freedom (N=7): {dof:,}")
    print(f"{'='*50}\n")

    # ================================================================
    # 12. WRITE OUTPUT
    # ================================================================
    gmsh.write(args.output)
    print(f"Mesh saved to: {args.output}")
    print(f"Visualise:     gmsh {args.output}")

    print(f"\nMesh format: GMSH MSH v4 (order {args.order})")
    print(f"Physical groups defined:")
    print(f"  1 = fluid (volume)")
    print(f"  2 = wall (aerofoil)")
    print(f"  3 = inflow (left + top + bottom far-field)")
    print(f"  4 = outflow (right boundary)")
    print(f"  5 = periodicZ0 (z=0 face)")
    print(f"  6 = periodicZ1 (z={args.z_span} face)")

    if args.gui:
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate 3D NACA 0012 hex mesh for NekRS / Nek5000",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Calibrated mesh family (final dissertation values, nz=4):
  M2 (~ 5,076 hex):  --lc-wall 0.04   --lc-far 2.0  --lc-wake 0.2   -o naca0012_M2.msh
  M3 (~10,504 hex):  --lc-wall 0.028  --lc-far 1.4  --lc-wake 0.14  -o naca0012_M3.msh
  M4 (~20,060 hex):  --lc-wall 0.02   --lc-far 1.1  --lc-wake 0.1   -o naca0012_M4.msh
  M5 (~40,396 hex):  --lc-wall 0.013  --lc-far 0.8  --lc-wake 0.07  -o naca0012_M5.msh

Workflow:
  1. Test 2D first:  add --mesh-2d --gui, check quad count, iterate lc-* values
  2. Generate 3D:    drop --mesh-2d, keep same lc-* values, set --nz 4
  3. Convert:        gmsh2nek (produces .re2 readable by both Nek5000 and NekRS)
""")

    # Mesh sizing
    parser.add_argument("--lc-wall", type=float, default=0.02,
                        help="Element size at aerofoil wall [default: 0.02c, the M4 value]")
    parser.add_argument("--lc-far",  type=float, default=1.1,
                        help="Element size at far-field    [default: 1.1c, the M4 value]")
    parser.add_argument("--lc-wake", type=float, default=0.1,
                        help="Element size in wake region [default: 0.1c, the M4 value]")

    # Domain
    parser.add_argument("--x-in",     type=float, default=-5.0,
                        help="Inlet x-coordinate   [default: -5c]")
    parser.add_argument("--x-out",    type=float, default=16.0,
                        help="Outlet x-coordinate  [default: 16c]")
    parser.add_argument("--y-extent", type=float, default=5.0,
                        help="Domain half-height   [default: 5c]")

    # Spanwise (3D)
    parser.add_argument("--nz",     type=int,   default=4,
                        help="Number of spanwise layers [default: 4]")
    parser.add_argument("--z-span", type=float, default=0.2,
                        help="Spanwise domain length    [default: 0.2c]")

    # Geometry
    parser.add_argument("--n-pts", type=int, default=200,
                        help="Points per aerofoil half-surface [default: 200]")
    parser.add_argument("--order", type=int, default=2,
                        help="Mesh element order [default: 2]")

    # Output
    parser.add_argument("-o", "--output", default="naca0012.msh",
                        help="Output mesh filename [default: naca0012.msh]")
    parser.add_argument("--mesh-2d",   action="store_true",
                        help="Generate 2D mesh only (for testing element count)")
    parser.add_argument("--subdivide", action="store_true",
                        help="Force all-quad by subdividing triangles (~3x count)")
    parser.add_argument("--gui", action="store_true",
                        help="Open GMSH GUI after meshing for visual inspection")

    args = parser.parse_args()
    create_mesh(args)
