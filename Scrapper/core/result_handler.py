import pandas as pd
import datetime

from config import OUTPUT_FILE


class ResultHandler:

    def __init__(self):
        self.data = []

    # ===========================
    # ADD RESULT
    # ===========================
    def add(self, result):
        if result is None:
            return

        if "timestamp" not in result:
            result["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        self.data.append(result)

    # ===========================
    # SAVE (PIVOT FORMAT)
    # ===========================
    def save(self):
        if not self.data:
            print("No data to save.")
            return

        df = pd.DataFrame(self.data)

        # ✅ pivot: site → columns
        pivot_df = df.pivot_table(
            index="model",
            columns="site",
            values="price",
            aggfunc="first"
        )

        # ✅ flatten columns
        pivot_df.columns.name = None
        pivot_df.reset_index(inplace=True)

        # ✅ add latest timestamp per model
        time_df = df.groupby("model")["timestamp"].max().reset_index()
        final_df = pivot_df.merge(time_df, on="model", how="left")

        # ✅ column order
        cols = ["model"] + [c for c in final_df.columns if c not in ["model", "timestamp"]] + ["timestamp"]
        final_df = final_df[cols]

        # ✅ filename
        filename = OUTPUT_FILE.replace(
            ".xlsx",
            f"_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )

        final_df.to_excel(filename, index=False)

        print(f"\n📂 Saved results: {filename}")