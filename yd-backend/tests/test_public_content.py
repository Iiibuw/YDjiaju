"""阶段 4（M5）前台 public 接口冒烟测试（banners/categories/downloads/about）。"""


def test_public_banners(client):
    r = client.get("/api/v1/public/banners")
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["data"], list)


def test_public_categories(client):
    r = client.get("/api/v1/public/categories")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert len(data) >= 4  # 种子 4 个分类
    kinds = {c["kind"] for c in data}
    assert {"space", "series", "category"} <= kinds


def test_public_downloads(client):
    r = client.get("/api/v1/public/downloads")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert "items" in data and "total" in data


def test_public_about(client):
    r = client.get("/api/v1/public/about-sections")
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["data"], list)
