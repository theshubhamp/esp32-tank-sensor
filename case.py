"""Parametric drop-in-lid enclosure for a Seeed XIAO ESP32-S3 tank sensor.

All dimensions in mm. Coordinate system: Z up, origin centred in X/Y, z=0
at the bottom face; x spans XMIN (-14.4, USB end) to XMAX (+14.4, cable
end). The board lies flat (21 mm length along X, USB-C edge facing -X) and
rests on two side rails; two full-length crush rails beside its edges
clamp it in a friction fit (no clips, no relief slots). A USB-C plug
passes through the -X wall (metal shell only, moulded boot outside).

The u.FL flex antenna (measured pad 37.5 x 17.5 mm, ~1.3 mm thick with its
adhesive foam) mounts fully inside: the case is 25 mm taller than the
board bay needs (inner 44 mm, outer 28.8 x 25.8 x 46.4) and the pad stands
vertically glued to the slide cover's inner face, z 4.2-41.7. The board
rails end short of the +X end so pad, board and rails clear each other.
No pass-through hole; the pigtail loops off the board's u.FL connector.

The six jumper wires to the sensors exit through the top face via a single
drop-shaped (teardrop-shaped in plan) vertical hole centred on it; the top
face is otherwise completely solid - a full roof over the cavity.

The +X end face (opposite the USB-C punch) is fully open - the whole
cavity cross-section - so the board slides straight in, and a slide cover
closes the face: it rides on rail fins protruding from the roof and floor
at the mouth (45-degree underside on the top fin), friction ribs on its
top/bottom edges crush 0.08 against the roof and floor, it enters through
a slot in the +y side wall, and an edge lip plugs that slot flush when
closed. The -y side-wall inner face is the slide stop.

Printability (Z-up, no supports, no floating cantilevers): rail undersides
and the top fin underside are 45-degree faces, and the roof underside is a
single perimeter-supported plane that bridges the cavity across the 21 mm
side-wall span (both side walls run full height, so every roof edge rests
on a wall). The cover prints flat (rotated on export); the antenna zone is
empty space inside.

Exported STLs: case_body.stl, case_lid.stl
"""

import math

import cadquery as cq

# ---- Seeed XIAO ESP32-S3 (measured) --------------------------------------
BOARD_L = 21.0        # PCB length, along X
BOARD_W = 17.5        # PCB width, along Y
PCB_T = 1.6
USB_SHELL_W = 9.0     # USB-C plug metal shell
USB_SHELL_H = 2.6

# ---- enclosure ------------------------------------------------------------
WALL = 2.4
FLOOR = 2.4
INNER_L = 24.0        # 3.0 slack past the board for the USB-C plug
INNER_W = 21.0        # 1.75 slack each side of the board
INNER_H = 44.0        # 19.0 board/wire headroom + 25.0 for the vertical antenna

RAIL_FACE = 8.0       # rail inner face: 16.0 gap, board overhangs 0.75/side
RAIL_TOP = 7.4        # board bottom plane (FLOOR + 5.0)

# antenna mount (no geometry - free volume only): the pad stands vertically
# glued to the cover's inner face (x = 12.5), y-centred, z 4.2-41.7; the
# board rails end short to clear it and the cover rail fins at the mouth
# sit below/above it (bottom fin top 3.9, top fin underside 43.1);
# assumes pad thickness with foam <= 1.3 mm
ANT_PAD_L = 37.5      # measured pad length (stands vertically)
ANT_PAD_W = 17.5      # measured pad width (across Y; cover face is 21 wide)
ANT_PAD_T = 1.3       # assumed max thickness incl. adhesive
RAIL_X1 = 10.3        # board rails end here (board edge is at 10.5)

# full-length friction rails clamping the board edges: a tall thin rail
# stands on each support-rail top beside the board edge for the whole
# board length, crushing BOARD_RIB_CRUSH per side; the thin-tall section
# keeps per-length stiffness low, and a 45-degree funnel chamfer at the
# +X (mouth) end feeds each board edge in as the board slides end-first
# (all bodies print overhang-free)
GRIP_X0 = -BOARD_L / 2                    # -10.5: rails span the board
GRIP_X1 = RAIL_X1                         # 10.3: flush with the rail ends
BOARD_RIB_T = 0.45      # rail thickness in Y; with 5.2 mm of flex height a
                        # rail bends ~0.5 mm (1 mm both sides) at ~3-4 N in
                        # PETG, so board/print variance absorbs as flex
BOARD_RIB_CRUSH = 0.05  # nominal interference against the board edge, per side
BOARD_RIB_TOP = 12.6    # rails: 5.2 mm of flex height above the rail tops
GRIP_LEAD = 0.5         # funnel chamfer on the rails' +X inner corners

# USB-C pass-through: metal shell only, moulded boot stays outside;
# 0.5 mm clearance per side so the plug slides in freely after printing
USB_CUT_W = USB_SHELL_W + 1.0   # 10.0
USB_CUT_H = USB_SHELL_H + 1.0   # 3.6
USB_Z = RAIL_TOP + PCB_T + USB_SHELL_H / 2   # 10.3: shell sits on the board top

# jumper-wire pass-through: one drop-shaped (teardrop) hole punched
# vertically through the solid roof, centred on the Z face; a vertical
# hole prints cleanly with any outline - the drop shape is cosmetic only
WIRE_HOLE_D = 5.3     # hex bundle of 6 x 1.6 mm jumper wires needs ~3.5 mm
WIRE_HOLE_XC = 0.0    # hole centre X: exact centre of the top face

# slide cover closing the fully open +X end face (the wall opposite the
# USB-C punch): the whole cavity cross-section is the mouth; triangular
# rail fins protrude from the roof (45-degree underside) and floor at the
# mouth and back the cover's top/bottom edges; friction ribs on those
# edges crush 0.08 against the roof/floor; the cover enters through a
# slot in the +y side wall and a full-height lip on its +y edge plugs the
# slot flush when closed; the -y side-wall inner face is the slide stop.
COVER_T = 1.8         # cover plate thickness (along X)
COVER_X0 = 12.5       # cover inner face (antenna pad glues here)
ROOF_T = 1.8          # solid roof: Z face fully solid except the teardrop
FIN_P = 1.5           # rail-fin depth along X
FIN_X_FACE = COVER_X0  # fin support face (coincident, contact face)
FIN_X0 = FIN_X_FACE - FIN_P                       # 11.0
FIN_T = 1.5           # fin height along Z at each end of the mouth
COVER_Y_HW = 10.42    # cover half width (0.08 ease per side in the mouth)
COVER_Z0 = FLOOR + 0.15                           # 2.55
COVER_Z1 = FLOOR + INNER_H - ROOF_T - 0.15        # 44.45
COVER_RIB_OUT = 0.23  # stand proud of the edge: 0.08 crush + 0.15 clearance
COVER_RIB_L = 5.0
COVER_RIB_YC = (-7.5, -2.5, 2.5, 7.5)
LIP_Y1 = 12.9         # lip plugs the entry slot flush with the side wall
SLOT_Y0 = 10.4        # slot cut slightly wider than the lip for free slide
# roof underside plane and mouth ceiling
CAVITY_TOP = FLOOR + INNER_H - ROOF_T         # 44.6

OUTER_W = INNER_W + 2 * WALL
XMIN = -(INNER_L / 2 + WALL)    # -14.4, USB end outer face
XMAX = -XMIN                    # +14.4, end opened for the slide cover
OUTER_L = XMAX - XMIN           # 28.8
OUTER_H = FLOOR + INNER_H       # 46.4
HW = INNER_W / 2


def build_case():
    case = (
        cq.Workplane("XY", origin=(XMIN, 0, 0))
        .box(OUTER_L, OUTER_W, OUTER_H, centered=(False, True, False))
    )
    cavity = (
        cq.Workplane("XY", origin=(XMIN + WALL, 0, FLOOR))
        .box(INNER_L, INNER_W, INNER_H - ROOF_T, centered=(False, True, False))
    )
    case = case.cut(cavity)
    # open mouth: remove the +X wall over the whole cavity cross-section;
    # 0.05 bite into the corner posts keeps boolean faces clean
    mouth = (
        cq.Workplane("XY")
        .box(WALL + 0.5, INNER_W + 0.1, INNER_H - ROOF_T,
             centered=(False, True, False))
        .translate((XMIN + WALL + INNER_L - 0.3, 0, FLOOR))
    )
    case = case.cut(mouth)
    case = case.edges("|Z").filter(
        lambda e: (abs(e.Center().x - XMIN) < 0.01 or abs(e.Center().x - XMAX) < 0.01)
        and abs(abs(e.Center().y) - OUTER_W / 2) < 0.01
    ).chamfer(0.6)

    # side rails the board rests on, ending at RAIL_X1 so the vertical
    # antenna pad on the cover's inner face clears them
    pos_rail = (
        cq.Workplane("XY")
        .box(RAIL_X1 - (XMIN + WALL), HW - RAIL_FACE, RAIL_TOP - FLOOR,
             centered=(False, False, False))
        .translate((XMIN + WALL, RAIL_FACE, FLOOR))
    )
    neg_rail = cq.Workplane(obj=pos_rail.val().mirror(mirrorPlane="XZ"))
    case = case.union(pos_rail).union(neg_rail)

    # full-length crush rails clamping the board edges: plain tall thin
    # walls on the rail tops, no clips or relief slots needed
    rib_face = BOARD_W / 2 - BOARD_RIB_CRUSH
    for sgn in (1, -1):
        y0 = rib_face if sgn > 0 else -rib_face - BOARD_RIB_T
        grip = (
            cq.Workplane("XY")
            .box(GRIP_X1 - GRIP_X0, BOARD_RIB_T, BOARD_RIB_TOP - RAIL_TOP,
                 centered=(False, False, False))
            .translate((GRIP_X0, y0, RAIL_TOP))
        )
        case = case.union(grip)
    # 45-degree lead-in on the rail top inner edges so the board glides
    # between the rails instead of stabbing into flat tops
    rib_top_edges = [
        e for e in case.val().Edges()
        if abs(e.Center().z - BOARD_RIB_TOP) < 0.01
        and abs(abs(e.Center().y) - rib_face) < 0.05
    ]
    case = case.newObject(rib_top_edges).chamfer(0.4)
    # 45-degree funnel chamfer on each rail's +X inner corner so the board
    # edges feed in as the board slides in end-first from the open mouth
    lead_edges = [
        e for e in case.val().Edges()
        if abs(e.Center().x - GRIP_X1) < 0.01
        and abs(abs(e.Center().y) - rib_face) < 0.06
        and e.Length() > 3.0
    ]
    case = case.newObject(lead_edges).chamfer(GRIP_LEAD)

    # USB-C pass-through in the -X wall (slot + round caps = oval)
    slot_len = USB_CUT_W - USB_CUT_H
    usb = (
        cq.Workplane("XY")
        .box(2 * WALL, slot_len, USB_CUT_H, centered=(True, True, False))
        .translate((XMIN, 0, USB_Z - USB_CUT_H / 2))
    )
    for dy in (slot_len / 2, -slot_len / 2):
        cap = (
            cq.Workplane("YZ")
            .circle(USB_CUT_H / 2)
            .extrude(2 * WALL)
            .translate((XMIN - WALL, dy, USB_Z))
        )
        usb = usb.union(cap)
    case = case.cut(usb)
    usb_edges = [
        e for e in case.val().Edges()
        if e.Center().x < XMIN + 0.6
        and abs(e.Center().y) < USB_CUT_W / 2 + 0.1
        and USB_Z - USB_CUT_H / 2 - 0.5 < e.Center().z < USB_Z + USB_CUT_H / 2 + 0.5
    ]
    case = case.newObject(usb_edges).chamfer(0.2)

    # jumper-wire teardrop punch through the solid roof: drop-shaped hole
    # in plan (apex pointing at the +X lid-entry wall), centred on the
    # top face
    wire_r = WIRE_HOLE_D / 2
    a = wire_r * math.cos(math.radians(45))
    hole_c = (
        cq.Workplane("XY", origin=(WIRE_HOLE_XC, 0, CAVITY_TOP - 0.6))
        .circle(wire_r)
        .extrude(OUTER_H + 0.6 - (CAVITY_TOP - 0.6))
    )
    hole_a = (
        cq.Workplane("XY", origin=(0, 0, CAVITY_TOP - 0.6))
        .polyline([
            (WIRE_HOLE_XC + a, a),
            (WIRE_HOLE_XC + a, -a),
            (WIRE_HOLE_XC + wire_r * math.sqrt(2), 0),
        ])
        .close()
        .extrude(OUTER_H + 0.6 - (CAVITY_TOP - 0.6))
    )
    case = case.cut(hole_c.union(hole_a))

    # cover rails at the mouth: fins protruding from the roof and floor,
    # backing the cover's top/bottom edge strips. The top fin is a pure
    # 45-degree triangle (no down-facing surface); the bottom fin stands
    # on the floor. Both bury into the corner posts for stiffness.
    top_fin = (
        cq.Workplane("XZ", origin=(0, HW + 0.1, 0))
        .polyline([
            (FIN_X_FACE, CAVITY_TOP - FIN_T),
            (FIN_X0, CAVITY_TOP),
            (FIN_X_FACE, CAVITY_TOP),
        ])
        .close()
        .extrude(2 * HW + 0.25)
    )
    bot_fin = (
        cq.Workplane("XY", origin=(FIN_X0, -(HW + 0.15), FLOOR))
        .box(FIN_P, 2 * HW + 0.25, FIN_T, centered=(False, False, False))
    )
    case = case.union(top_fin).union(bot_fin)

    # entry slot through the +y side wall: the cover (and its sealing lip)
    # slides in through here; the lip plugs it flush when closed
    entry = (
        cq.Workplane("XY", origin=(FIN_X_FACE - 0.05, SLOT_Y0, FLOOR - 0.1))
        .box(XMAX + 0.2 - (FIN_X_FACE - 0.05), OUTER_W / 2 + 0.12 - SLOT_Y0,
             INNER_H - ROOF_T + 0.2, centered=(False, False, False))
    )
    case = case.cut(entry)

    return case


def build_lid():
    """Slide cover for the open +X end, vertical in use, exported flat.
    The plate sits in the mouth plane resting against the rail-fin faces;
    ribs on its top/bottom edges crush 0.08 against the roof/floor for
    retention; the full-height lip on the +y edge plugs the side-wall
    entry slot flush when closed, and the -y plate edge meets the side
    wall as the slide stop. Antenna pad glues to the inner face."""
    lid = (
        cq.Workplane("XY", origin=(COVER_X0, -COVER_Y_HW, COVER_Z0))
        .box(COVER_T, 2 * COVER_Y_HW, COVER_Z1 - COVER_Z0,
             centered=(False, False, False))
    )
    lip = (
        cq.Workplane("XY", origin=(COVER_X0, COVER_Y_HW, COVER_Z0))
        .box(COVER_T, LIP_Y1 - COVER_Y_HW, COVER_Z1 - COVER_Z0,
             centered=(False, False, False))
    )
    lid = lid.union(lip)
    for yc in COVER_RIB_YC:
        for sgn in (1, -1):     # +1: top edge ribs, -1: bottom edge ribs
            z0 = COVER_Z1 if sgn > 0 else COVER_Z0 - COVER_RIB_OUT
            rib = (
                cq.Workplane("XY", origin=(COVER_X0, yc - COVER_RIB_L / 2, z0))
                .box(COVER_T, COVER_RIB_L, COVER_RIB_OUT,
                     centered=(False, False, False))
            )
            lid = lid.union(rib)
    # lay flat for printing: rotate so the plate normal (+X) points up,
    # antenna face (x=COVER_X0) ends on the bed, then shift to the origin
    lid = lid.rotate((0, 0, 0), (0, 1, 0), -90)
    lid = lid.translate((COVER_Z1 + COVER_RIB_OUT, 0, -COVER_X0))
    return lid


def main():
    case = build_case()
    lid = build_lid()
    cq.exporters.export(case.val(), "case_body.stl", tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(lid.val(), "case_lid.stl", tolerance=0.05, angularTolerance=0.1)


if __name__ == "__main__":
    main()
