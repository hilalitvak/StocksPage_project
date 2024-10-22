CREATE VIEW DiversInvestors AS
    (SELECT I.ID
    FROM Investor I JOIN Buying B ON I.ID = B.ID
    WHERE B.tDate IN (SELECT B1.tDate FROM Buying B1
                        LEFT OUTER JOIN Company C1 on B1.Symbol = C1.Symbol
                        WHERE I.ID= B1.ID
                        GROUP BY B1.ID, B1.tDate
                        HAVING COUNT(DISTINCT C1.Sector)>=6)
    GROUP BY I.ID);


CREATE VIEW DiversInvestorsAmount AS
    (SELECT B.ID, ROUND(SUM(B.BQuantity * S.Price),3) AS TotalShares
    FROM Buying B JOIN Stock S on B.tDate = S.tDate AND B.Symbol = S.Symbol
    GROUP BY B.ID);


CREATE VIEW part1_companies AS
    (SELECT DISTINCT C.Symbol, C.Sector
    FROM Company C JOIN Buying B on C.Symbol = B.Symbol
    WHERE NOT EXISTS(SELECT DISTINCT tDate From Buying
                            EXCEPT SELECT DISTINCT tDate FROM Buying B1
                            WHERE C.Symbol = B1.Symbol ));


CREATE VIEW PopularCompanies AS
    (SELECT C.Symbol, C.Sector
    FROM part1_companies C
    WHERE NOT EXISTS(SELECT C1.Symbol FROM part1_companies C1
                    WHERE C1.Symbol <> C.Symbol AND C1.Sector = C.Sector));


CREATE VIEW InvestorsInPopularCompany AS
    (SELECT C.Symbol, I.ID, SUM(B.BQuantity) AS TotalShares
    FROM Investor I JOIN Buying B ON I.ID = B.ID
    JOIN PopularCompanies C ON B.Symbol = C.Symbol
    GROUP BY C.Symbol, I.ID);


CREATE VIEW [ProfitableCompanies] AS
    SELECT DISTINCT S1.Symbol
    FROM Stock S1, Stock S2
    WHERE S1.tDate IN (Select Dates.LastDate From Dates) AND
          S1.Price > 1.06 * (
                                SELECT S3.Price FROM Stock S3 WHERE S1.Symbol = S3.Symbol
                                                                    AND S3.tDate IN (SELECT Dates.FirstDate FROM Dates)
                            ); ---1.06 * the price of the company on the first tDate


CREATE VIEW [InvestorsPerCompany] AS
    SELECT B1.ID as ID, B1.Symbol as Symbol
    FROM Buying B1
    JOIN ProfitableCompanies P1 ON P1.Symbol = B1.Symbol
    WHERE B1.tDate IN (SELECT Dates.FirstDate FROM Dates);


CREATE VIEW [Dates] AS
    SELECT S2.tDate AS LastDate, S1.tDate AS FirstDate
    FROM Stock S1, Stock S2
    WHERE S1.tDate <= ALL(SELECT S3.tDate FROM Stock S3 WHERE S3.Symbol=S1.Symbol) AND S2.tdate >= ALL(SELECT S4.tDate FROM Stock S4 WHERE S2.Symbol=S4.Symbol);

