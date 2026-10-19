"""Fictional CSV contract lesson. No external calls or imports."""
import csv
import io

EXPECTED = ["document_id", "customer_po_number", "quantity"]


def validate(text):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != EXPECTED:
        raise ValueError("Column contract changed: " + repr(reader.fieldnames))
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Row width does not match header")
    return rows


def migrate_known_v2(text):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ["document_id", "purchase_order_number", "quantity"]:
        raise ValueError("Not the approved v2 contract")
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=EXPECTED)
    writer.writeheader()
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed v2 row")
        writer.writerow({"document_id": row["document_id"],
                         "customer_po_number": row["purchase_order_number"],
                         "quantity": row["quantity"]})
    return out.getvalue()


if __name__ == "__main__":
    v1 = "document_id,customer_po_number,quantity\ndemo-1,00123,0\n"
    v2 = "document_id,purchase_order_number,quantity\ndemo-1,00123,0\n"
    assert validate(v1)[0]["customer_po_number"] == "00123"
    try:
        validate(v2)
    except ValueError as exc:
        print("EXPECTED STOP:", exc)
    else:
        raise AssertionError("Unapproved schema accepted")
    assert validate(migrate_known_v2(v2)) == validate(v1)
    for row in ["x,1", "x,1,2,extra"]:
        try:
            migrate_known_v2("document_id,purchase_order_number,quantity\n" + row + "\n")
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed row accepted")
    print("PASS: explicit migration preserved document ID, leading zeros and zero quantity")
