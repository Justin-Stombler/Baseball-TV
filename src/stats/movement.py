##pitch movement math, kept separate from rendering so the plot math is testable/reusable.

##average MLB strike zone: ~17in wide (plate width), ~25in tall — used as the real-world
##extents for the strike-zone-shaped movement view (half-extents since 0,0 is the box center).
STRIKE_ZONE_HALF_WIDTH_IN = 17.0 / 2
STRIKE_ZONE_HALF_HEIGHT_IN = 25.0 / 2


def normalize_break_circle(hb_in: float | None, ivb_in: float | None, scale_in: float = 26.0) -> tuple[float, float]:
    """Convert horizontal/induced-vertical break (inches) into (x, y) fractions in [-1, 1]
    for plotting on a circular movement chart, where `scale_in` inches of break = the circle's edge.

    x = horizontal break fraction (positive = arm-side per statcast's hb_in sign)
    y = vertical break fraction (positive = rise/less drop)

    Missing values are treated as 0. Combined magnitude is clamped to the unit circle
    (values beyond `scale_in` inches sit right on the edge instead of overflowing it).
    """
    x = (hb_in or 0.0) / scale_in
    y = (ivb_in or 0.0) / scale_in
    magnitude = (x ** 2 + y ** 2) ** 0.5
    if magnitude > 1:
        x /= magnitude
        y /= magnitude
    return x, y


def break_magnitude_fraction(hb_in: float | None, ivb_in: float | None, scale_in: float = 26.0) -> float:
    """0-1 fraction of the movement scale used by the combined break vector, for color intensity."""
    x, y = normalize_break_circle(hb_in, ivb_in, scale_in)
    return min(1.0, (x ** 2 + y ** 2) ** 0.5)


def normalize_to_zone(
    x_in: float | None,
    y_in: float | None,
    half_width_in: float = STRIKE_ZONE_HALF_WIDTH_IN,
    half_height_in: float = STRIKE_ZONE_HALF_HEIGHT_IN,
) -> tuple[float, float]:
    """Convert an (x, y) offset from zone center (inches) into (x, y) fractions in [-1, 1]
    for plotting inside a strike-zone-shaped box, where `half_width_in`/`half_height_in`
    inches reach that axis's edge. Used for plate location (plate_x/plate_z); works for any
    inches-from-center pair.

    Each axis is clamped independently (a pitch 30in off the plate sideways but only 5in
    high sits on the box's side edge, not the corner of a circle).
    """
    x = (x_in or 0.0) / half_width_in
    y = (y_in or 0.0) / half_height_in
    x = max(-1.0, min(1.0, x))
    y = max(-1.0, min(1.0, y))
    return x, y

