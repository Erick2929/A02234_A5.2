"""Module to compute total sales cost from a price catalogue and sales."""
# pylint: disable=invalid-name

import time
import sys
import json


def read_json(filepath):
    """Reads the provided json file and returns its contents."""
    with open(filepath, "r", encoding="utf-8") as read_file:
        file_info = json.load(read_file)
    return file_info


def build_price_map(catalogue):
    """Builds a dict mapping product title to price."""
    price_map = {}
    for item in catalogue:
        title = item.get("title")
        price = item.get("price")
        if title is None or price is None:
            print(f"WARNING: Skipping invalid catalogue entry: {item}")
            continue
        if not isinstance(price, (int, float)) or price < 0:
            print(f"WARNING: Invalid price for '{title}': {price}. Skipping.")
            continue
        price_map[title] = price
    return price_map


def compute_sales(sales, price_map):
    """Computes total cost per sale and overall total."""
    results = []
    grand_total = 0.0

    for sale in sales:
        sale_id = sale.get("SALE_ID", "UNKNOWN")
        customer = sale.get("Customer", "UNKNOWN")
        items = sale.get("Items", [])
        sale_total = 0.0

        for item in items:
            product = item.get("Product")
            quantity = item.get("Quantity", 0)

            if product not in price_map:
                print(f"ERROR: Product '{product}' not found in catalogue "
                      f"(Sale: {sale_id}). Skipping.")
                continue
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                print(f"WARNING: Invalid quantity for '{product}' "
                      f"(Sale: {sale_id}): {quantity}. Skipping.")
                continue

            sale_total += price_map[product] * quantity

        grand_total += sale_total
        results.append({
            "sale_id": sale_id,
            "customer": customer,
            "total": sale_total
        })

    return results, grand_total


def format_output(results, grand_total, elapsed_time):
    """Formats the results into a human-readable string."""
    lines = []
    lines.append("=" * 50)
    lines.append("           SALES RESULTS REPORT")
    lines.append("=" * 50)

    for result in results:
        lines.append(f"Sale ID  : {result['sale_id']}")
        lines.append(f"Customer : {result['customer']}")
        lines.append(f"Total    : ${result['total']:,.2f}")
        lines.append("-" * 50)

    lines.append(f"GRAND TOTAL: ${grand_total:,.2f}")
    lines.append("=" * 50)
    lines.append(f"Execution time: {elapsed_time:.4f} seconds")

    return "\n".join(lines)


def main():
    """Computes the total cost for all sales."""
    if len(sys.argv) < 3:
        print("Usage: python computeSales.py "
              "priceCatalogue.json salesRecord.json")
        sys.exit(1)

    catalogue_file = sys.argv[1]
    sales_file = sys.argv[2]

    start_time = time.time()

    try:
        catalogue = read_json(catalogue_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR reading catalogue file: {e}")
        sys.exit(1)

    try:
        sales = read_json(sales_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR reading sales file: {e}")
        sys.exit(1)

    price_map = build_price_map(catalogue)
    results, grand_total = compute_sales(sales, price_map)

    end_time = time.time()
    elapsed_time = end_time - start_time

    output = format_output(results, grand_total, elapsed_time)

    print(output)

    with open("SalesResults.txt", "w", encoding="utf-8") as out_file:
        out_file.write(output)

    print("\nResults saved to SalesResults.txt")


if __name__ == "__main__":
    main()
