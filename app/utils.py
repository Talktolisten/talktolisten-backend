from datetime import datetime
from sqlalchemy.sql.sqltypes import Date

# Format DOB from MM / DD / YYYY (str) -> YYYY-MM-DD (Date)
def format_dob(dob_str: str) -> Date:
    dob_date = datetime.strptime(dob_str, "%m / %d / %Y").date()
    return dob_date

# Format DOB from YYYY-MM-DD (Date) -> MM / DD / YYYY (str)
def format_dob_str(dob_date: Date) -> str:
    dob_str = dob_date.strftime("%m / %d / %Y")
    return dob_str