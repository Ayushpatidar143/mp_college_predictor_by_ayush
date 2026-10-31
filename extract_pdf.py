import pdfplumber
import pandas as pd

pdf_path = "data.pdf"
all_rows = []

print("Extracting all data from PDF thoroughly, please wait...")

with pdfplumber.open(pdf_path) as pdf:
  for i, page in enumerate(pdf.pages):
    print(f"Reading page {i+1}...")

    # 1. Extract standard tables
    tables = page.extract_tables()
    for table in tables:
      for row in table:
        row_str = str(row).lower()
        # Skip header/title rows
        if (
            not row
            or all(cell is None or cell == "" for cell in row)
            or "directorate" in row_str
            or "bachelor of technology" in row_str
            or "opening closing rank" in row_str
            or "s. no." in row_str
            or "inst_name" in row_str
        ):
          continue
        all_rows.append(row)

# Convert to DataFrame
if all_rows:
  df = pd.DataFrame(all_rows)
  # Drop completely duplicate rows if any
  df = df.drop_duplicates()
  df.to_csv("mp_cutoff.csv", index=False, header=False)
  print(
      "🎉 Success! Complete cutoff data has been saved to 'mp_cutoff.csv' (Total"
      f" rows: {len(df)})"
  )
else:
  print("No tables found, please check the PDF format.")