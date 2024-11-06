import helper_functions
import config
import constants
import mappers
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("tenant_config_migration_assets | START")


# Compare the two assets to check if we need to do a PUT
def is_asset_same(asset, destination_asset):
    referenceId = asset["name"]
    for dest_asset in destination_asset:
        if referenceId == dest_asset["name"]:
            #   need to delete these to compare asset content
            del asset["id"]
            del dest_asset["id"]
            del asset["securityClassification"]
            del dest_asset["securityClassification"]
            if asset == dest_asset:
                return True
            else:
                return False
    return False


# GET all assets
domain_1_assets_results = helper_functions.get_request(
    config.start_domain, constants.ENDPOINT_ASSETS, config.start_head
)
domain_2_assets_results = helper_functions.get_request(
    config.post_domain, constants.ENDPOINT_ASSETS, config.post_head
)

# GET all security classifications
domain_1_sc_results = helper_functions.get_request(
    config.start_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, config.start_head
)
domain_2_sc_results = helper_functions.get_request(
    config.post_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, config.post_head
)

# MAP assets to objects and collect matches
mapped_domain_1_assets_results = mappers.map_assets(domain_1_assets_results)
mapped_domain_2_assets_results = mappers.map_assets(domain_2_assets_results)
asset_matches = helper_functions.find_matches(
    mapped_domain_1_assets_results, mapped_domain_2_assets_results, "name"
)

# MAP security classifications to objects and collect matches
mapped_domain_1_sc_results = mappers.map_security_classifications(domain_1_sc_results)
mapped_domain_2_sc_results = mappers.map_security_classifications(domain_2_sc_results)
sc_matches = helper_functions.find_matches(
    mapped_domain_1_sc_results, mapped_domain_2_sc_results, "name"
)

# Begin migration
for asset_domain_1 in mapped_domain_1_assets_results:
    # Find security classification ID in destination domain
    sc_id = sc_matches[asset_domain_1["securityClassification"]["name"]]

    # Build asset to send
    asset_to_send = {
        "name": asset_domain_1["name"],
        "description": asset_domain_1["description"],
        "securityClassification": {"id": sc_id},
    }

    # Decide whether to PUT
    if asset_domain_1["name"] in asset_matches:
        # Check if the two ASSETs are the same
        if is_asset_same(asset_domain_1, mapped_domain_2_assets_results) is False:
            uuid = asset_matches[asset_domain_1["name"]]
            print(asset_to_send)
            helper_functions.put_request(
                uuid,
                asset_to_send,
                config.post_domain + constants.ENDPOINT_ASSETS,
                config.post_head,
            )

    # Else POST
    else:
        helper_functions.post_request(
            asset_to_send,
            config.post_domain + constants.ENDPOINT_ASSETS,
            config.post_head,
        )

logging.info("tenant_config_migration_assets | END")