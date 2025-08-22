"""
Version management for Claude Model Manager
"""

__version__ = "1.0.2"  # 这是应用的固定版本号


def get_current_version():
    """Get the current application version"""
    return __version__


def parse_version(version_str):
    """Parse version string into tuple for comparison"""
    import re

    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")

    # Parse semantic version (major.minor.patch[-prerelease])
    match = re.match(
        r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$",
        version_str,
    )

    if not match:
        return (0, 0, 0, "")

    major, minor, patch, prerelease = match.groups()

    # Convert to integers
    version_tuple = (int(major), int(minor), int(patch))

    # Handle prerelease
    if prerelease:
        # Split prerelease into parts for proper comparison
        prerelease_parts = []
        for part in prerelease.split("."):
            if part.isdigit():
                prerelease_parts.append(int(part))
            else:
                prerelease_parts.append(part)
        version_tuple = version_tuple + (prerelease_parts,)
    else:
        version_tuple = version_tuple + (None,)

    return version_tuple


def compare_versions(current, latest):
    """
    Compare two version strings
    Returns: -1 if current < latest, 0 if equal, 1 if current > latest
    """
    current_tuple = parse_version(current)
    latest_tuple = parse_version(latest)

    # Compare major, minor, patch
    for i in range(3):
        if current_tuple[i] < latest_tuple[i]:
            return -1
        elif current_tuple[i] > latest_tuple[i]:
            return 1

    # Compare prerelease
    current_prerelease = current_tuple[3]
    latest_prerelease = latest_tuple[3]

    if current_prerelease is None and latest_prerelease is None:
        return 0
    elif current_prerelease is None:
        return 1  # Release version is greater than prerelease
    elif latest_prerelease is None:
        return -1  # Prerelease is less than release

    # Compare prerelease parts
    for i in range(max(len(current_prerelease), len(latest_prerelease))):
        if i >= len(current_prerelease):
            return -1
        elif i >= len(latest_prerelease):
            return 1

        current_part = current_prerelease[i]
        latest_part = latest_prerelease[i]

        if isinstance(current_part, int) and isinstance(latest_part, int):
            if current_part < latest_part:
                return -1
            elif current_part > latest_part:
                return 1
        elif isinstance(current_part, int):
            return -1  # Number < string
        elif isinstance(latest_part, int):
            return 1  # String > number
        else:
            if current_part < latest_part:
                return -1
            elif current_part > latest_part:
                return 1

    return 0
