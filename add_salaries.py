from models import User, Salary
from datetime import datetime

def add_salaries():
    # Get the user
    user = User.get_by_username('nik2000')
    if not user:
        print("User not found")
        return

    # Salary data
    salaries = [
        ('June 2022', 79128),
        ('July 2022', 39793),
        ('August 2022', 39793),
        ('September 2022', 39793),
        ('October 2022', 39793),
        ('November 2022', 39793),
        ('December 2022', 39773),
        ('January 2023', 39793),
        ('February 2023', 39793),
        ('March 2023', 39793),
        ('April 2023', 40033),
        ('May 2023', 40033),
        ('June 2023', 40033),
        ('July 2023', 44616),
        ('August 2023', 44616),
        ('September 2023', 44616),
        ('October 2023', 44616),
        ('November 2023', 44616),
        ('December 2023', 44596),
        ('January 2024', 44616),
        ('February 2024', 44616),
        ('March 2024', 48616),
        ('April 2024', 63284),
        ('May 2024', 50783),
        ('June 2024', 50783),
        ('July 2024', 50783),
        ('August 2024', 50783),
        ('September 2024', 50783),
        ('October 2024', 50783),
        ('November 2024', 50783),
        ('December 2024', 50763),
        ('January 2025', 50783),
        ('February 2025', 50783),
        ('March 2025', 50783),
        ('April 2025', 76983)
    ]

    # Add each salary record
    for month_year, amount in salaries:
        # Parse the date
        date = datetime.strptime(month_year, '%B %Y')
        # Create the salary record
        Salary.create(amount, date, user.id)
        print(f"Added salary for {month_year}: ₹{amount}")

if __name__ == '__main__':
    add_salaries() 