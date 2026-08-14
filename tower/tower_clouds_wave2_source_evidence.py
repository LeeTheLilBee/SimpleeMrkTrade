"""
GP073–GP075 Wave 2 source contract bootstrap evidence.

IMPORTANT:
These records prove source-owned summary contract seams.
They do not prove operational business systems or live feeds.
"""


CLOUDS_ADAPTER_CERTIFICATION_BRANCH = (
    "clouds-rebuild-dev"
)

CLOUDS_ADAPTER_CERTIFICATION_COMMIT = (
    "9606ccef44045634eaf977f1df641751aefd866b"
)


WAVE2_SOURCE_EVIDENCE = {

    "teller": {

        "pack":
        "GP073",

        "source_id":
        "teller",

        "source_label":
        "The Teller",

        "source_contract_version":
        "teller-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-teller-v1",

        "base_branch":
        "tower-teller-vault-handoff-dev",

        "base_commit_observed":
        "2a30e280489642465362fa48adf47c9067d976e9",

        "publisher_branch":
        "teller-clouds-source-wave2",

        "publisher_commit":
        "3a04683e74aafba24d89a4904d84fb73ccdc6a3f",

        "package_preexisting":
        False,

        "publisher_sha256":
        "811d3224139ff11728ab75ad3f0005d55583a9315bc923146bdf48e2e89ded04",

        "source_contract_bootstrap_ready":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "operational_system_verified":
        False,

        "real_business_data_connected":
        False,

        "source_endpoint_available":
        False,

        "real_live_connection":
        False,
    },


    "grounds": {

        "pack":
        "GP074",

        "source_id":
        "grounds",

        "source_label":
        "The Grounds",

        "source_contract_version":
        "grounds-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-grounds-v1",

        "base_branch":
        "main",

        "base_commit_observed":
        "4acd633e671d05a1137cfbcba0361bc779273fbe",

        "publisher_branch":
        "grounds-clouds-source-wave2",

        "publisher_commit":
        "4034f967d714b9db44016ea8dfba380ddd95b0a0",

        "package_preexisting":
        False,

        "publisher_sha256":
        "3a37ae258501b6d3e6e71e504a87a655a6df6ef54f76e03d4ead2d111c8b86aa",

        "source_contract_bootstrap_ready":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "operational_system_verified":
        False,

        "real_business_data_connected":
        False,

        "source_endpoint_available":
        False,

        "real_live_connection":
        False,
    },


    "atm_operations": {

        "pack":
        "GP075",

        "source_id":
        "atm_operations",

        "source_label":
        "ATM Operations",

        "source_contract_version":
        "atm-operations-clouds-summary-v1",

        "adapter_id":
        "clouds-adapter-atm-operations-v1",

        "base_branch":
        "main",

        "base_commit_observed":
        "4acd633e671d05a1137cfbcba0361bc779273fbe",

        "publisher_branch":
        "atm-operations-clouds-source-wave2",

        "publisher_commit":
        "9f5aa9f220b4cd72bc54ff200a46dcacdf985fac",

        "package_preexisting":
        False,

        "publisher_sha256":
        "4eaf284871f30c8aef9b8578160b76fb2ec4c4de98ac7499072f912367a80cf4",

        "source_contract_bootstrap_ready":
        True,

        "source_local_tests_passed":
        True,

        "signed_transport_certified":
        True,

        "clouds_adapter_certified":
        True,

        "operational_system_verified":
        False,

        "real_business_data_connected":
        False,

        "source_endpoint_available":
        False,

        "real_live_connection":
        False,
    },
}
