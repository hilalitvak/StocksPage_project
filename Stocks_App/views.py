from django.shortcuts import render
from django.db import connection
from datetime import datetime
from. models import *


def index(request):
    return render(request, 'index.html')


def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def Add_Transaction(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TOP 10 *
            FROM Transactions
            ORDER BY tDate DESC, ID DESC
        """)
        sql_res1 = dictfetchall(cursor)
    return render(request, 'Add_Transaction.html', {'sql_res1': sql_res1})


def input_Transaction(request):
    input_ID = request.POST['id']
    input_Sum = request.POST['sum']
    flag_duplicate = False
    with connection.cursor() as cursor:
        flag_id = False  # Set a flag to indicate if the provided ID does not exist
        cursor.execute("""
            SELECT ID
            FROM Investor
            WHERE ID = %s;
            """, [request.POST["id"]])
        sql_id = dictfetchall(cursor)

        cursor.execute("""
                    SELECT TOP 1 tDate
                    FROM Stock ORDER BY tDate DESC;
                    """, )
        time = dictfetchall(cursor)[0]['tDate']
        # If the provided ID does not exist, set a flag
        if not sql_id:  # If the provided ID does not exist, set a flag
            flag_id = True
        else:  # Check if a transaction for today and the provided ID already exists
            cursor.execute("""
                   SELECT ID
                   FROM Transactions
                   WHERE tDate = %s AND ID = %s;
            """, [time, input_ID])
            existing_transaction = dictfetchall(cursor)

            # If a transaction exists for today and the provided ID, update it
            if existing_transaction:  # If a transaction exists for today and the provided ID, update it
                flag_duplicate = True
            else:   # If a transaction does not exist for today and the provided ID
            # Insert new transaction and update the investor's amount
                cursor.execute("""
                               INSERT INTO Transactions (tDate, ID, TAmount)
                               VALUES (%s, %s, %s);
                           """, [time, input_ID, input_Sum])

                cursor.execute("""
                               UPDATE Investor
                               SET Amount = Amount + %s
                               WHERE ID = %s;
                           """, [input_Sum, input_ID])

        # Fetch top 10 transactions for rendering updated
        cursor.execute("""
                   SELECT TOP 10 *
                   FROM Transactions
                   ORDER BY tDate DESC, ID DESC;
               """)
        sql_res1 = dictfetchall(cursor)
    return render(request, 'Add_Transaction.html', {'sql_res1': sql_res1, 'flag_id': flag_id, 'flag_duplicate':flag_duplicate})


def Buy_Stocks(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                         SELECT TOP 10 B.tDate, ID, S.Symbol, BQuantity 
                         FROM Buying B JOIN Stock S on S.Symbol = B.Symbol and S.tDate = B.tDate
                         ORDER BY tDate DESC, ID DESC, Symbol ASC 
                """)
        sql_res2 = dictfetchall(cursor)
    return render(request, 'Buy_Stocks.html', {'sql_res2': sql_res2})


def input_stock(request):
    input_ID = request.POST['id']
    input_Symbol = request.POST['company']
    input_Quantity = request.POST['quantity']
    with connection.cursor() as cursor:
        id_flag = False
        company_flag = False
        sum_flag = False
        dup_flag = False
        # Extract results from the SQL query
        cursor.execute(""" SELECT ID FROM Investor WHERE ID = %s;
            """, [input_ID])
        sql_res_id = dictfetchall(cursor)
        cursor.execute(""" SELECT Symbol FROM Stock WHERE Symbol = %s; """, [input_Symbol])
        sql_res_company = dictfetchall(cursor)
        # Check if the stock exists for today's date
        cursor.execute("""SELECT TOP 1 tDate
                                FROM Stock
                                ORDER BY tDate DESC
                                """,)
        sql_res_time = dictfetchall(cursor)[0]['tDate']
        # Now check if the investor has already bought the stock for today's date
        cursor.execute("""SELECT * 
                        FROM Buying
                        WHERE Symbol = %s AND ID = %s AND tDate = %s
                """, [input_Symbol, input_ID, sql_res_time])
        sql_res_duplicate = dictfetchall(cursor)
        # If the provided ID does not exist, set a flag
        if not sql_res_id:
            id_flag = True
        if not sql_res_company:  # If the provided company does not exist, set a flag
            company_flag = True
        if sql_res_duplicate: # If there's a duplicate buy, set a flag
            dup_flag = True
        # If the provided ID and company exist and there is no duplicate buy, check if the investor has enough cash to buy the stocks
        if sql_res_id and sql_res_company and not sql_res_duplicate:
            cursor.execute("""
                        SELECT Price
                        FROM Stock
                        WHERE Symbol = %s AND tDate=%s
                    """, [input_Symbol, sql_res_time])
            result_stock_price = dictfetchall(cursor) # Fetch the price of the stock
            stock_price = result_stock_price[0]['Price']
            if(not result_stock_price):# Check if result_stock_price is not empty
                sum_flag = True
            else:
                  # Extract the price from the first dictionary
                cursor.execute("""
                               SELECT Amount
                               FROM Investor
                               WHERE ID = %s AND Amount >= %s * %s
                           """, [input_ID, stock_price, input_Quantity])
                sql_res = dictfetchall(cursor) #select the investor's available cash
                # If the investor has enough cash to buy the stocks, set a flag
                if not sql_res:
                    sum_flag = True # If the investor does not have enough cash to buy the stocks, set a flag
                else:
                    # Insert the buying record for the investor and the stock with the quantity of stocks bought by the investor for today's date
                    cursor.execute("""
                        INSERT INTO Buying (tDate, ID, Symbol, BQuantity)
                        VALUES (%s, %s, %s, %s)
                    """, [sql_res_time, input_ID, input_Symbol, input_Quantity])

                    # Update the investor's available cash by subtracting the amount of money spent on buying the stocks from the investor's available cash
                    cursor.execute("""
                        UPDATE Investor
                        SET Amount = Amount - %s * %s
                        WHERE ID = %s
                    """, [stock_price, input_Quantity, input_ID])
# top 10 buying records for rendering updated
    with connection.cursor() as cursor:
        cursor.execute("""
                 SELECT TOP 10 B.tDate, ID, S.Symbol, BQuantity 
                 FROM Buying B LEFT JOIN Stock S on S.Symbol = B.Symbol and S.tDate = B.tDate
                 ORDER BY tDate DESC, ID DESC, Symbol ASC
        """)
        sql_res2 = dictfetchall(cursor)
    return render(request, 'Buy_Stocks.html',
                  {'sql_res2': sql_res2, 'id_flag': id_flag, 'company_flag': company_flag, 'sum_flag': sum_flag,
                   'dup_flag': dup_flag})


def Query_Results(request):
    # Execute your database query here
    with connection.cursor() as cursor:
        # answar to the first query
        cursor.execute("""SELECT I.Name, D2.TotalShares as TotalSum
                        FROM Investor I JOIN DiversInvestors D ON I.ID=D.ID
                        LEFT JOIN DiversInvestorsAmount D2 on I.ID = D2.ID
                        ORDER BY TotalShares DESC;""")
        sql_resA = dictfetchall(cursor)
        # answar to the second query
        cursor.execute("""SELECT I.Symbol, I1.Name, I.TotalShares as Quantity
                            FROM InvestorsInPopularCompany I JOIN Investor I1 ON I.ID = I1.ID
                            WHERE I.TotalShares >= ALL
                                  (SELECT TotalShares FROM InvestorsInPopularCompany WHERE I.Symbol = Symbol)
                            ORDER BY I.Symbol, I1.Name ;""")
        sql_resB = dictfetchall(cursor)

        # answar to the third query
        cursor.execute("""SELECT COALESCE(IPC.Symbol, PC.Symbol) AS Symbol, COALESCE(COUNT(DISTINCT IPC.ID), 0) AS TotalInvestors
                            FROM ProfitableCompanies PC
                            LEFT OUTER JOIN InvestorsPerCompany IPC ON PC.Symbol = IPC.Symbol
                            GROUP BY COALESCE(IPC.Symbol, PC.Symbol)
                            ORDER BY Symbol; """)
        sql_resC = dictfetchall(cursor)

    return render(request, 'Query_Results.html', {'sql_resA': sql_resA, 'sql_resB': sql_resB, 'sql_resC': sql_resC})
