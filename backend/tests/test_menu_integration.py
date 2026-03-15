from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.service import Service, ServiceCategory


client = TestClient(app)


def create_category_and_service(db, *, category_name: str, service_name: str, is_active: bool = True):
    category = ServiceCategory(name=category_name, is_active=True, order_index=0)
    db.add(category)
    db.flush()

    service = Service(
        name=service_name,
        category_id=category.id,
        is_active=is_active,
        order_index=0,
    )
    db.add(service)
    db.commit()
    db.refresh(category)
    db.refresh(service)
    return category, service


def delete_test_data(db, category_ids, service_ids):
    if service_ids:
        db.query(Service).filter(Service.id.in_(service_ids)).delete(synchronize_session=False)
    if category_ids:
        db.query(ServiceCategory).filter(ServiceCategory.id.in_(category_ids)).delete(synchronize_session=False)
    db.commit()


def test_menu_tree_hides_inactive_services():
    db = SessionLocal()
    category_ids = []
    service_ids = []
    try:
        # создаём активную и неактивную услугу в одном разделе
        cat, active_service = create_category_and_service(db, category_name="[TEST] Меню", service_name="[TEST] Активная", is_active=True)
        _, inactive_service = create_category_and_service(db, category_name="[TEST] Меню 2", service_name="[TEST] Скрытая", is_active=False)
        category_ids.extend([cat.id])
        service_ids.extend([active_service.id, inactive_service.id])

        response = client.get("/api/v1/menu/tree")
        assert response.status_code == 200
        data = response.json()

        # в дереве не должно быть неактивных услуг
        all_services = []
        for node in data:
            for svc in node.get("services", []):
                all_services.append(svc["name"])
        assert "[TEST] Активная" in all_services
        assert "[TEST] Скрытая" not in all_services
    finally:
        delete_test_data(db, category_ids, service_ids)
        db.close()


def test_services_endpoint_respects_is_active():
    db = SessionLocal()
    category_ids = []
    service_ids = []
    try:
        cat, active_service = create_category_and_service(db, category_name="[TEST] Категория", service_name="[TEST] Видимая", is_active=True)
        _, inactive_service = create_category_and_service(db, category_name="[TEST] Категория 2", service_name="[TEST] Невидимая", is_active=False)
        category_ids.append(cat.id)
        service_ids.extend([active_service.id, inactive_service.id])

        # список услуг
        list_response = client.get("/api/v1/services")
        assert list_response.status_code == 200
        names = [item["name"] for item in list_response.json()]
        assert "[TEST] Видимая" in names
        assert "[TEST] Невидимая" not in names

        # детальная информация по ID неактивной услуги должна возвращать 404
        detail_response = client.get(f"/api/v1/services/{inactive_service.id}")
        assert detail_response.status_code == 404
    finally:
        delete_test_data(db, category_ids, service_ids)
        db.close()


