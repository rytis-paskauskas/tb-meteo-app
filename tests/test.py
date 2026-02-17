from tb_rest_client.rest_client_ce import RestClientCE
import meteoresampler


def test_import():
    assert meteoresampler is not None
    assert RestClientCE is not None 
