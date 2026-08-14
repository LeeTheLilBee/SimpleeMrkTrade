"""
GP070–GP071 source-owned publisher evidence.

Generated only after:
- source-local tests passed;
- source branches pushed;
- signed transport certification passed;
- actual Clouds GP060 adapter certification passed.

This record still does NOT claim a real external connection.
"""


WAVE1_SOURCE_EVIDENCE = {

    "tower": {

        "pack":
        "GP069",

        "source_id":
        "tower",

        "source_label":
        "The Tower",

        "source_contract_version":
        "tower-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-tower-v1",

        "publisher_branch":
        "tower-clouds-gp060-integration-dev",

        "publisher_module_path":
        "tower/tower_clouds_summary_publisher.py",

        "publisher_module_sha256":
        "7a49f28be971b48f8a659e9633b27a795630d817a500a14e170f23e809dc5418",

        "source_owned_publisher":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "external_source_connected":
        False,

        "external_connection_verified":
        False,

        "counts_as_real_live_connection":
        False,
    },


    "observatory": {

        "pack":
        "GP070",

        "source_id":
        "observatory",

        "source_label":
        "The Observatory",

        "source_contract_version":
        "observatory-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-observatory-v1",

        "source_base_branch":
        "ob-owner-experience-simplification",

        "source_base_head_observed":
        "5f3ec16cda70fb545c032971129ab3e8a706cc93",

        "publisher_branch":
        "ob-clouds-source-wave1",

        "publisher_commit":
        "98781c18ba433782592f2577196f60ff8b0ac1c0",

        "publisher_module_path":
        "ob_owner_experience/clouds_summary_publisher.py",

        "publisher_module_sha256":
        "92976ac89871c7ef7b578e270a120ac5d16f64784b5be9928d5d43b336180e8a",

        "source_owned_publisher":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "external_source_connected":
        False,

        "external_connection_verified":
        False,

        "counts_as_real_live_connection":
        False,
    },


    "archive_vault": {

        "pack":
        "GP071",

        "source_id":
        "archive_vault",

        "source_label":
        "Archive Vault",

        "source_contract_version":
        "archive-vault-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-archive-vault-v1",

        "source_base_branch":
        "vault-dev",

        "source_base_head_observed":
        "02bd0be321de7a7b45ac3ed0da74bd5ba174a1c5",

        "publisher_branch":
        "vault-clouds-source-wave1",

        "publisher_commit":
        "131facb2849773e64f6f3a2cd737b8e30db757be",

        "publisher_module_path":
        "vault/clouds_summary_publisher.py",

        "publisher_module_sha256":
        "44b5e3a42e42c352e2081ac0140006ccca521f92f56c3ea7bfbae598a2ad84ed",

        "source_owned_publisher":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "external_source_connected":
        False,

        "external_connection_verified":
        False,

        "counts_as_real_live_connection":
        False,
    },
}


CLOUDS_ADAPTER_CERTIFICATION_BRANCH = (
    "clouds-rebuild-dev"
)

CLOUDS_ADAPTER_CERTIFICATION_COMMIT = (
    "9606ccef44045634eaf977f1df641751aefd866b"
)
