from tb_rest_client.rest_client_ce import RestClientCE
from .identifiers import VALID_IDENTIFIERS


def fetch_data(identifier, start, end, config):
    info = VALID_IDENTIFIERS[identifier]

    with RestClientCE(base_url=config["endpoint"]) as client:
        client.login(
            username=config["username"],
            password=config["password"],
        )

        print(
            f"Fetching {identifier} data from {start} to {end}"
        )

        # TODO: Implement real TB telemetry query
        # For now return dummy data
        return [
            {"timestamp": start, "value": 0},
            {"timestamp": end, "value": 1},
        ]
