# Clara - Tests pour FSDriver
"""
Tests unitaires pour le driver filesystem
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from drivers.fs_driver import FSDriver, FSItem


@pytest.fixture
def temp_dir():
    """Crée un dossier temporaire pour les tests"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def fs_driver(temp_dir):
    """Crée une instance FSDriver pointant vers un dossier temporaire"""
    return FSDriver(root_path=temp_dir)


def test_write_read_text(fs_driver):
    """Test écriture et lecture de texte"""
    fs_driver.write_text("test.txt", "Hello, World!")
    content = fs_driver.read_text("test.txt")
    assert content == "Hello, World!"


def test_write_read_bytes(fs_driver):
    """Test écriture et lecture de bytes"""
    data = b"Binary data"
    fs_driver.write_bytes("test.bin", data)
    content = fs_driver.read_bytes("test.bin")
    assert content == data


def test_append_text(fs_driver):
    """Test ajout de texte"""
    fs_driver.write_text("test.txt", "Hello")
    fs_driver.append_text("test.txt", ", World!")
    content = fs_driver.read_text("test.txt")
    assert content == "Hello, World!"


def test_list_dir(fs_driver):
    """Test listage de dossier"""
    fs_driver.write_text("file1.txt", "content1")
    fs_driver.write_text("file2.txt", "content2")
    fs_driver.make_dir("subdir")
    
    items = fs_driver.list_dir("")
    assert len(items) >= 3
    
    paths = [item.path for item in items]
    assert "file1.txt" in paths
    assert "file2.txt" in paths
    assert "subdir" in paths


def test_make_dir(fs_driver):
    """Test création de dossier"""
    fs_driver.make_dir("test_dir")
    assert (fs_driver.root_path / "test_dir").is_dir()
    
    # Test avec exist_ok=True (ne doit pas planter)
    fs_driver.make_dir("test_dir", exist_ok=True)


def test_move_path(fs_driver):
    """Test déplacement de fichier"""
    fs_driver.write_text("source.txt", "content")
    fs_driver.move_path("source.txt", "dest.txt")
    
    assert not (fs_driver.root_path / "source.txt").exists()
    assert (fs_driver.root_path / "dest.txt").exists()
    assert fs_driver.read_text("dest.txt") == "content"


def test_delete_path_file(fs_driver):
    """Test suppression de fichier"""
    fs_driver.write_text("to_delete.txt", "content")
    fs_driver.delete_path("to_delete.txt")
    assert not (fs_driver.root_path / "to_delete.txt").exists()


def test_delete_path_dir(fs_driver):
    """Test suppression de dossier"""
    fs_driver.make_dir("to_delete_dir")
    fs_driver.write_text("to_delete_dir/file.txt", "content")
    fs_driver.delete_path("to_delete_dir")
    assert not (fs_driver.root_path / "to_delete_dir").exists()


def test_stat_path(fs_driver):
    """Test récupération d'infos sur un chemin"""
    fs_driver.write_text("test.txt", "content")
    stat = fs_driver.stat_path("test.txt")
    
    assert stat["exists"] is True
    assert stat["is_dir"] is False
    assert stat["size"] > 0
    assert "relative_path" in stat


def test_stat_path_nonexistent(fs_driver):
    """Test stat sur un fichier inexistant"""
    stat = fs_driver.stat_path("nonexistent.txt")
    assert stat["exists"] is False


def test_search_text(fs_driver):
    """Test recherche de texte"""
    fs_driver.write_text("file1.txt", "Hello world")
    fs_driver.write_text("file2.txt", "Goodbye world")
    fs_driver.write_text("file3.txt", "No match")
    
    results = fs_driver.search_text("world")
    assert len(results) == 2
    
    paths = [r["path"] for r in results]
    assert "file1.txt" in paths
    assert "file2.txt" in paths


def test_search_text_with_extensions(fs_driver):
    """Test recherche avec filtre d'extensions"""
    fs_driver.write_text("file1.txt", "Hello")
    fs_driver.write_text("file2.md", "Hello")
    fs_driver.write_text("file3.py", "Hello")
    
    results = fs_driver.search_text("Hello", extensions=[".txt", ".md"])
    assert len(results) == 2
    
    paths = [r["path"] for r in results]
    assert "file1.txt" in paths
    assert "file2.md" in paths
    assert "file3.py" not in paths


def test_path_confinement(fs_driver):
    """Test que le driver ne peut pas sortir du root"""
    with pytest.raises(ValueError, match="Path escapes root"):
        fs_driver._resolve("../../etc/passwd")


def test_write_text_overwrite(fs_driver):
    """Test écrasement de fichier"""
    fs_driver.write_text("test.txt", "old")
    fs_driver.write_text("test.txt", "new", overwrite=True)
    assert fs_driver.read_text("test.txt") == "new"


def test_write_text_no_overwrite(fs_driver):
    """Test refus d'écrasement"""
    fs_driver.write_text("test.txt", "old")
    with pytest.raises(FileExistsError):
        fs_driver.write_text("test.txt", "new", overwrite=False)

