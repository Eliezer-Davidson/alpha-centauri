"""Alpha Centauri — FAITHFUL PORT of the donor quadruped's leg IK.

Runs under .venv (numpy only). Source: MonashRobotics/DingoQuadruped (MIT),
dingo_ws/src/dingo_control/src/dingo_control/Kinematics.py + util.py, mirrored
locally for reference. interface_constants.extension_at() records that a
faithful port of this IK agrees with the donor to 1.6e-7 mm — so this file
PORTS, it does not re-derive. Every line of the solver below is the donor's,
with exactly three deviations, each marked D1/D2/D3 inline:

  D1  rospy is gone (logwarn removed — see D2).
  D2  THE SILENT CLIP IS A HARD REFUSAL. Dingo's Kinematics.py clips an
      over-extended request to 0.8*(L2+L3) and does NOT raise — an unreachable
      command silently slams the foot ~35-50 mm instead of erroring.
      interface_constants says our layer must refuse before it gets there
      (LEG_EXTENSION_LIMIT_FRAC = 0.97), so len_B beyond the limit raises
      ReachError instead of being clipped.
  D3  np.matrix -> np.ndarray in RotMatrix3D (deprecated API, same numbers).

The donor's own forward_kinematics() is NOT ported: its hard-coded angle
(403*pi)/4500 = 16.120 deg disagrees with its own phi complement
(90 - 73.91738698 = 16.083 deg) by 0.037 deg, i.e. the donor's FK is subtly
inconsistent with its IK. Verification here is done against MuJoCo's forward
kinematics of the exported model instead (crawl_sim.py, closed-loop grid
check), which is the geometry that actually gets simulated.

Config values are injected from the provenance snapshot the MJCF was exported
against, NOT re-imported live — the XML is baked, so the IK must match the
XML even if interface_constants.py has moved since (concurrent-edit law).

Leg indexing is the donor's: 0 = front-right, 1 = front-left, 2 = rear-right,
3 = rear-left (the docstring in the donor source says otherwise; the code's
is_right test and default_stance columns say this, and the code wins).
"""

import math

import numpy as np

TWO_PI = 2 * math.pi


class ReachError(ValueError):
    """Foot target beyond LEG_EXTENSION_LIMIT_FRAC of absolute reach (D2)."""


class DingoConfig:
    """The donor Configuration fields the IK reads, in metres/radians,
    values injected from the mjcf_export provenance snapshot."""

    def __init__(self, snap):
        self.L1 = snap["L1_HIP_OFFSET"] / 1000.0
        self.L2 = snap["L2_THIGH"] / 1000.0
        self.L3 = snap["L3_CALF"] / 1000.0
        self.phi = math.radians(snap["PHI_DEG"])
        self.LEG_FB = snap["LEG_FB"] / 1000.0
        self.LEG_LR = snap["LEG_LR"] / 1000.0
        self.limit_frac = snap["LEG_EXTENSION_LIMIT_FRAC"]
        # donor LEG_ORIGINS columns: FR, FL, BR, BL
        self.LEG_ORIGINS = np.array(
            [[self.LEG_FB, self.LEG_FB, -self.LEG_FB, -self.LEG_FB],
             [-self.LEG_LR, self.LEG_LR, -self.LEG_LR, self.LEG_LR],
             [0, 0, 0, 0]])


# ---------------------------------------------------------------- donor util
def point_to_rad(p1, p2):
    """converts 2D cartesian points to polar angles in range 0 - 2pi"""
    theta = math.atan2(p2, p1)
    return (theta + TWO_PI) % TWO_PI


def RotMatrix3D(rotation=(0, 0, 0), is_radians=True, order="xyz"):
    roll, pitch, yaw = rotation
    if not is_radians:                                    # pragma: no cover
        roll, pitch, yaw = map(math.radians, (roll, pitch, yaw))
    c, s = math.cos, math.sin
    rotX = np.array([[1, 0, 0],
                     [0, c(roll), -s(roll)],
                     [0, s(roll), c(roll)]])              # D3: ndarray
    rotY = np.array([[c(pitch), 0, s(pitch)],
                     [0, 1, 0],
                     [-s(pitch), 0, c(pitch)]])
    rotZ = np.array([[c(yaw), -s(yaw), 0],
                     [s(yaw), c(yaw), 0],
                     [0, 0, 1]])
    assert order == "xyz"
    return rotZ @ rotY @ rotX


# ------------------------------------------------------------- donor solver
def leg_explicit_inverse_kinematics(r_body_foot, leg_index, config):
    """Donor solver, verbatim structure. Input: foot position relative to the
    leg's first frame (the abduction axis), metres. Output: (theta_1, theta_2,
    theta_3) in the donor's servo convention."""
    if leg_index == 1 or leg_index == 3:
        is_right = 0
    else:
        is_right = 1

    x, y, z = r_body_foot[0], r_body_foot[1], r_body_foot[2]
    if is_right:
        y = -y
    r_body_foot = np.array([x, y, z])

    # rotate the origin frame in-line with config.L1 (rotation about x-axis)
    R1 = math.pi / 2 - config.phi
    rot_mtx = RotMatrix3D([-R1, 0, 0], is_radians=True)
    r_ = rot_mtx @ r_body_foot.reshape(3, 1)
    r_ = np.ravel(r_)
    x, y, z = r_

    len_A = np.linalg.norm([0, y, z])
    a_1 = point_to_rad(y, z)
    a_2 = math.asin(math.sin(config.phi) * config.L1 / len_A)
    a_3 = math.pi - a_2 - config.phi

    theta_1 = a_1 + a_3
    if theta_1 >= TWO_PI:
        theta_1 = np.mod(theta_1, TWO_PI)

    offset = np.array([0.0, config.L1 * math.cos(theta_1),
                       config.L1 * math.sin(theta_1)])
    translated_frame = r_ - offset

    R2 = theta_1 + config.phi - math.pi / 2
    rot_mtx = RotMatrix3D([-R2, 0, 0], is_radians=True)
    j4_2_vec_ = rot_mtx @ translated_frame.reshape(3, 1)
    j4_2_vec_ = np.ravel(j4_2_vec_)
    x_, y_, z_ = j4_2_vec_

    len_B = np.linalg.norm([x_, 0, z_])

    # D2: refuse, never clip. The donor clipped to 0.8*(L2+L3) silently.
    if len_B >= (config.L2 + config.L3) * config.limit_frac:
        raise ReachError(
            f"leg {leg_index}: target {r_body_foot} needs {len_B*1000:.1f} mm "
            f"in-plane, past {config.limit_frac:.2f} * "
            f"{(config.L2 + config.L3)*1000:.1f} mm")

    b_1 = point_to_rad(x_, z_)
    b_2 = math.acos((config.L2**2 + len_B**2 - config.L3**2)
                    / (2 * config.L2 * len_B))
    b_3 = math.acos((config.L2**2 + config.L3**2 - len_B**2)
                    / (2 * config.L2 * config.L3))

    theta_2 = b_1 - b_2
    theta_3 = math.pi - b_3

    return np.array(angle_corrector([theta_1, theta_2, theta_3]))


def four_legs_inverse_kinematics(r_body_foot, config):
    """columns FR, FL, BR, BL — donor order."""
    alpha = np.zeros((3, 4))
    for i in range(4):
        body_offset = config.LEG_ORIGINS[:, i]
        alpha[:, i] = leg_explicit_inverse_kinematics(
            r_body_foot[:, i] - body_offset, i, config)
    return alpha


def angle_corrector(angles=(0, 0, 0)):
    angles = list(angles)
    angles[0] = angles[0]
    angles[1] = angles[1] - math.pi        # theta2 offset
    angles[2] = angles[2] - math.pi / 2    # theta3 offset
    for index, theta in enumerate(angles):
        if theta > TWO_PI:
            angles[index] = np.mod(theta, TWO_PI)
        if theta > math.pi:
            angles[index] = -(TWO_PI - theta)
    return angles
