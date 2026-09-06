import pandas as pd
import random


def clean_number_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """return df"""
    df = df.copy()
    df[cols] = (
        df[cols]
        .astype(str)
        .map(
            lambda x: pd.to_numeric(
                x.replace(" ", "")
                .replace(",", "")
                .replace("，", "")
                .replace("￥", "")
                .strip(),
                errors="coerce",
            ),
            na_action="ignore",
        )
    )
    return df


def clean_percentage_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """return df"""
    df = df.copy()

    def clean(x):
        x = x.replace(" ", "").replace(",", "").replace("，", "").strip()
        if "%" in x or "％" in x:
            x = x.replace("%", "").replace("％", "")
            return pd.to_numeric(x, errors="coerce") / 100
        else:
            return pd.to_numeric(x, errors="coerce")

    df[cols] = df[cols].astype(str).map(clean, na_action="ignore")
    return df


def clean_date_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """return df"""
    df = df.copy()
    df[cols] = (
        df[cols]
        .astype(str)
        .map(
            lambda x: pd.to_datetime(
                x.replace("年", "-")
                .replace("月", "-")
                .replace("日", "")
                .replace("号", "")
                .replace(".", "-")
                .replace("/", "-")
                .replace("\\", "-")
                .strip(),
                errors="coerce",
            ),
            na_action="ignore",
        )
    )
    return df


def clean_str_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """return df"""
    df = df.copy()
    df[cols] = (
        df[cols].astype(str).map(lambda x: x.strip(), na_action="ignore").astype(str)
    )
    return df


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """return df"""
    df = df.copy()
    df.columns = df.columns.astype(str).map(lambda x: x.replace(" ", "").strip())
    return df


class Cleandf:
    """def __init__(self,df:pd.DataFrame) -> None:
    self.df=df.copy()"""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def clean_number_cols(self, cols: list[str]) -> "Cleandf":
        """return self"""
        raw = self.df[cols]
        self.df = clean_number_cols(self.df, cols)

        cleanbool = raw.notna() & self.df[cols].isna()
        cleaninfor = cleanbool.sum()
        cleanresult = cleaninfor[cleaninfor > 0]
        if len(cleanresult) != 0:
            print("\n<clean number error>")
            for col in cleanresult.index:
                total = sum(raw[col].notna())
                count = cleanresult[col]
                mark = cleanbool[col]
                values = raw[col][mark]
                allsample = values.unique().tolist()
                sample = random.sample(allsample, min(5, len(allsample)))
                print(
                    f'"{col}"：notna values {total}，error values {count}，sample {sample}，allsample {len(allsample)}；'
                )
            option = input("quit -> .* | coerce na -> c：")
            if option != "c":
                raise Exception("clean df error")
        return self

    def clean_percentage_cols(self, cols: list[str]) -> "Cleandf":
        """return self"""
        raw = self.df[cols]
        self.df = clean_percentage_cols(self.df, cols)

        cleanbool = raw.notna() & self.df[cols].isna()
        cleaninfor = cleanbool.sum()
        cleanresult = cleaninfor[cleaninfor > 0]
        if len(cleanresult) != 0:
            print("\n<clean percentage error>")
            for col in cleanresult.index:
                total = sum(raw[col].notna())
                count = cleanresult[col]
                mark = cleanbool[col]
                values = raw[col][mark]
                allsample = values.unique().tolist()
                sample = random.sample(allsample, min(5, len(allsample)))
                print(
                    f'"{col}"：notna values {total}，error values {count}，sample {sample}，allsample {len(allsample)}；'
                )
            option = input("quit -> .* | coerce na -> c：")
            if option != "c":
                raise Exception("clean df error")
        return self

    def clean_date_cols(self, cols: list[str]) -> "Cleandf":
        """return self"""
        raw = self.df[cols]
        self.df = clean_date_cols(self.df, cols)

        cleanbool = raw.notna() & self.df[cols].isna()
        cleaninfor = cleanbool.sum()
        cleanresult = cleaninfor[cleaninfor > 0]
        if len(cleanresult) != 0:
            print("\n<clean date error>")
            for col in cleanresult.index:
                total = sum(raw[col].notna())
                count = cleanresult[col]
                mark = cleanbool[col]
                values = raw[col][mark]
                allsample = values.unique().tolist()
                sample = random.sample(allsample, min(5, len(allsample)))
                print(
                    f'"{col}"：notna values {total}，error values {count}，sample {sample}，allsample {len(allsample)}；'
                )
            option = input("quit -> .* | coerce na -> c：")
            if option != "c":
                raise Exception("clean df error")
        return self

    def clean_str_cols(self, cols: list[str]) -> "Cleandf":
        """return self"""
        self.df = clean_str_cols(self.df, cols)
        return self

    def clean_columns(self) -> "Cleandf":
        """return self"""
        self.df = clean_columns(self.df)
        return self
