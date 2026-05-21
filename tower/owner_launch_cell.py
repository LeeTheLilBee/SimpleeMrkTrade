from __future__ import annotations

import json
from typing import Any, Dict

from tower.owner_access_launcher import create_owner_tower_launch


def build_owner_tower_launch_packet(
    *,
    actor_user_id: str = 'owner_solice',
    target_user_id: str = 'owner_solice',
    session_id: str = 'session_owner_launcher',
    device_id: str = 'device_owner_primary',
    ttl_seconds: int = 20 * 60,
    include_regenerate: bool = False,
    base_url: str = '',
) -> Dict[str, Any]:
    packet = create_owner_tower_launch(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        session_id=session_id,
        device_id=device_id,
        ttl_seconds=ttl_seconds,
        include_regenerate=include_regenerate,
        base_url=base_url,
        reason='Owner launch cell requested temporary Tower access URLs.',
    )
    return packet


def print_owner_tower_launch_cell(
    *,
    actor_user_id: str = 'owner_solice',
    target_user_id: str = 'owner_solice',
    session_id: str = 'session_owner_launcher',
    device_id: str = 'device_owner_primary',
    ttl_seconds: int = 20 * 60,
    include_regenerate: bool = False,
    base_url: str = '',
) -> Dict[str, Any]:
    packet = build_owner_tower_launch_packet(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        session_id=session_id,
        device_id=device_id,
        ttl_seconds=ttl_seconds,
        include_regenerate=include_regenerate,
        base_url=base_url,
    )

    print('=' * 80)
    print('THE TOWER — OWNER LAUNCH LINKS')
    print('=' * 80)

    if not packet.get('ok'):
        print(json.dumps(packet, indent=2, sort_keys=True))
        return packet

    print('Temporary scoped keycards issued.')
    print('Expires in seconds:', packet.get('expires_in_seconds'))
    print('Session:', packet.get('session_id'))
    print('Device:', packet.get('device_id'))
    print()
    print('Use these links inside your running Flask/Colab app:')
    print()

    urls = packet.get('urls', {})
    for key in ['entry', 'command', 'status', 'regenerate']:
        if key in urls:
            print(key.upper() + ':')
            print(urls[key])
            print()

    print('Safety note: these links contain temporary scoped keycards. Do not share them publicly.')
    return packet


if __name__ == '__main__':
    print_owner_tower_launch_cell()
