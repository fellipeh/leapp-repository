import pytest

from leapp.exceptions import StopActorExecution
from leapp.libraries.actor.library import scan_repositories
from leapp import reporting
from leapp.libraries.common.testutils import produce_mocked, create_report_mocked
from leapp.libraries.stdlib import api
from leapp.models import RepositoriesMap, RepositoryMap


def test_scan_valid_file(monkeypatch):
    monkeypatch.setattr(api, 'produce', produce_mocked())
    scan_repositories('files/tests/sample01.csv')

    assert api.produce.called == 1
    assert len(api.produce.model_instances) == 1
    assert isinstance(api.produce.model_instances[0], RepositoriesMap)
    assert len(api.produce.model_instances[0].repositories) == 4
    assert isinstance(api.produce.model_instances[0].repositories[0], RepositoryMap)
    assert api.produce.model_instances[0].repositories[0].from_id == 'FromRepo01'
    assert api.produce.model_instances[0].repositories[0].repo_type == 'rpm'
    assert isinstance(api.produce.model_instances[0].repositories[3], RepositoryMap)
    assert api.produce.model_instances[0].repositories[3].to_id == 'ToRepo04'
    assert api.produce.model_instances[0].repositories[3].arch == 'ppc64le'


def test_repository_mapping_file_not_found(monkeypatch):
    def file_not_exists(_filepath):
        return False
    monkeypatch.setattr('os.path.isfile', file_not_exists)
    monkeypatch.setattr(reporting, 'create_report', create_report_mocked())
    with pytest.raises(StopActorExecution):
        scan_repositories('/etc/leapp/files/repomap.csv')
    assert reporting.create_report.called == 1
    assert 'inhibitor' in reporting.create_report.report_fields['flags']
    assert 'Repositories map file not found' in reporting.create_report.report_fields['title']


def test_scan_empty_file(monkeypatch):
    monkeypatch.setattr(reporting, 'create_report', create_report_mocked())
    with pytest.raises(StopActorExecution):
        scan_repositories('files/tests/sample02.csv')
    assert reporting.create_report.called == 1
    assert 'inhibitor' in reporting.create_report.report_fields['flags']
    assert 'Repositories map file is invalid' in reporting.create_report.report_fields['title']


def test_scan_invalid_file_txt(monkeypatch):
    monkeypatch.setattr(reporting, 'create_report', create_report_mocked())
    with pytest.raises(StopActorExecution):
        scan_repositories('files/tests/sample03.csv')
    assert reporting.create_report.called == 1
    assert 'inhibitor' in reporting.create_report.report_fields['flags']
    assert 'Repositories map file is invalid' in reporting.create_report.report_fields['title']


def test_scan_invalid_file_csv(monkeypatch):
    monkeypatch.setattr(reporting, 'create_report', create_report_mocked())
    with pytest.raises(StopActorExecution):
        scan_repositories('files/tests/sample04.csv')
    assert reporting.create_report.called == 1
    assert 'inhibitor' in reporting.create_report.report_fields['flags']
    assert 'Repositories map file is invalid' in reporting.create_report.report_fields['title']
