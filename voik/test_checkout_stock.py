"""Stock is checked and decremented on checkout."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Usuario, Producto, Compra, DetalleCompra
from app import process_checkout, _parse_cart_qty


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def seed(db):
    user = Usuario(
        nombre="Test",
        nombre_usuario="tester",
        email="tester@example.com",
        clave="secret",
        rol="cliente",
    )
    product = Producto(nombre="Auriculares", precio=1000.0, existencia=2)
    db.add_all([user, product])
    db.commit()
    db.refresh(user)
    db.refresh(product)
    return user, product


def test_parse_cart_qty():
    assert _parse_cart_qty(3) == 3
    assert _parse_cart_qty("2") == 2
    assert _parse_cart_qty(0) == 0
    assert _parse_cart_qty(-1) == 0
    assert _parse_cart_qty("nope") == 0


def test_checkout_decrements_stock():
    db = make_session()
    user, product = seed(db)

    compra, error = process_checkout(db, user.id, {str(product.id): 2})
    assert error is None
    assert compra is not None
    db.refresh(product)
    assert product.existencia == 0
    assert db.query(Compra).count() == 1
    assert db.query(DetalleCompra).count() == 1


def test_checkout_rejects_over_stock():
    db = make_session()
    user, product = seed(db)

    compra, error = process_checkout(db, user.id, {str(product.id): 3})
    assert compra is None
    assert "suficiente existencia" in error
    db.refresh(product)
    assert product.existencia == 2
    assert db.query(Compra).count() == 0


if __name__ == "__main__":
    test_parse_cart_qty()
    test_checkout_decrements_stock()
    test_checkout_rejects_over_stock()
    print("ok")
