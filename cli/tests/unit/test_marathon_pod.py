import dcoscli.marathon.main as main
from dcos import marathon
from dcos.errors import DCOSException

import pytest
from mock import create_autospec, patch


def test_pod_add_invoked_successfully():
    _assert_pod_add_invoked_successfully(pod_file_json={"arbitrary": "json"})
    _assert_pod_add_invoked_successfully(pod_file_json=["more", "json"])


def test_pod_add_propagates_exceptions_from_add_pod():
    _assert_pod_add_propagates_exceptions_from_add_pod(DCOSException('BOOM!'))
    _assert_pod_add_propagates_exceptions_from_add_pod(Exception('Oops!'))


def test_pod_remove_invoked_successfully():
    _assert_pod_remove_invoked_successfully(pod_id='a-pod', force=False)
    _assert_pod_remove_invoked_successfully(pod_id='a-pod', force=True)
    _assert_pod_remove_invoked_successfully(pod_id='b-pod', force=False)


def test_pod_remove_propagates_exceptions_from_remove_pod():
    _assert_pod_remove_propagates_exceptions_from_remove_pod(
        DCOSException('BOOM!'))
    _assert_pod_remove_propagates_exceptions_from_remove_pod(
        Exception('Oops!'))


def test_pod_show_invoked_successfully():
    _assert_pod_show_invoked_successfully(pod_json={'id': 'a-pod', 'foo': 1})
    _assert_pod_show_invoked_successfully(pod_json={'id': 'b-pod', 'bar': 2})


def test_pod_show_propagates_exceptions_from_show_pod():
    _assert_pod_show_propagates_exceptions_from_show_pod(
        DCOSException('BOOM!'))
    _assert_pod_show_propagates_exceptions_from_show_pod(
        Exception('Oops!'))


def test_pod_list_success_case():
    marathon_client = create_autospec(marathon.Client)

    subcmd = main.MarathonSubcommand(_unused_resource_reader,
                                     lambda: marathon_client)
    returncode = subcmd.pod_list(json_=False)

    assert returncode == 0
    marathon_client.list_pod.assert_called_with()


def _assert_pod_add_invoked_successfully(pod_file_json):
    pod_file_path = "some/path/to/pod.json"
    resource_reader = {pod_file_path: pod_file_json}.__getitem__
    marathon_client = create_autospec(marathon.Client)

    subcmd = main.MarathonSubcommand(resource_reader, lambda: marathon_client)
    returncode = subcmd.pod_add(pod_file_path)

    assert returncode == 0
    marathon_client.add_pod.assert_called_with(pod_file_json)


def _assert_pod_add_propagates_exceptions_from_add_pod(exception):
    def resource_reader(path):
        return {"some": "json"}

    marathon_client = create_autospec(marathon.Client)
    marathon_client.add_pod.side_effect = exception

    subcmd = main.MarathonSubcommand(resource_reader, lambda: marathon_client)
    with pytest.raises(exception.__class__) as exception_info:
        subcmd.pod_add('does/not/matter')

    assert exception_info.value == exception


def _assert_pod_remove_invoked_successfully(pod_id, force):
    marathon_client = create_autospec(marathon.Client)

    subcmd = main.MarathonSubcommand(
        resource_reader=_unused_resource_reader,
        create_marathon_client=lambda: marathon_client)
    returncode = subcmd.pod_remove(pod_id, force)

    assert returncode == 0
    marathon_client.remove_pod.assert_called_with(pod_id, force)


def _assert_pod_remove_propagates_exceptions_from_remove_pod(exception):
    marathon_client = create_autospec(marathon.Client)
    marathon_client.remove_pod.side_effect = exception

    subcmd = main.MarathonSubcommand(
        resource_reader=_unused_resource_reader,
        create_marathon_client=lambda: marathon_client)
    with pytest.raises(exception.__class__) as exception_info:
        subcmd.pod_remove('does/not/matter', force=False)

    assert exception_info.value == exception


@patch('dcoscli.marathon.main.emitter', autospec=True)
def _assert_pod_show_invoked_successfully(emitter, pod_json):
    marathon_client = create_autospec(marathon.Client)
    marathon_client.show_pod.return_value = pod_json

    subcmd = main.MarathonSubcommand(
        resource_reader=_unused_resource_reader,
        create_marathon_client=lambda: marathon_client)

    returncode = subcmd.pod_show(pod_json['id'])

    assert returncode == 0
    marathon_client.show_pod.assert_called_with(pod_json['id'])
    emitter.publish.assert_called_with(pod_json)


def _assert_pod_show_propagates_exceptions_from_show_pod(exception):
    marathon_client = create_autospec(marathon.Client)
    marathon_client.show_pod.side_effect = exception

    subcmd = main.MarathonSubcommand(
        resource_reader=_unused_resource_reader,
        create_marathon_client=lambda: marathon_client)
    with pytest.raises(exception.__class__) as exception_info:
        subcmd.pod_show('does/not/matter')

    assert exception_info.value == exception


def _unused_resource_reader(path):
    assert False, "should not be called"
