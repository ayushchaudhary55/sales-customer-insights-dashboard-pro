-- Sales & Customer Insights Dashboard SQL Queries
SELECT SUM(Sales) AS Total_Sales, SUM(Profit) AS Total_Profit, COUNT(DISTINCT Order_ID) AS Total_Orders, SUM(Sales)/COUNT(DISTINCT Order_ID) AS Average_Order_Value FROM sales_orders;
SELECT Region, SUM(Sales) AS Total_Sales, SUM(Profit) AS Total_Profit FROM sales_orders GROUP BY Region ORDER BY Total_Sales DESC;
SELECT Product_Category, SUM(Sales) AS Total_Sales, SUM(Profit) AS Total_Profit FROM sales_orders GROUP BY Product_Category ORDER BY Total_Sales DESC;
SELECT Product_Name, SUM(Sales) AS Total_Sales FROM sales_orders GROUP BY Product_Name ORDER BY Total_Sales DESC LIMIT 10;
SELECT strftime('%Y-%m', Order_Date) AS Month, SUM(Sales) AS Monthly_Sales FROM sales_orders GROUP BY Month ORDER BY Month;
SELECT Payment_Mode, SUM(Sales) AS Total_Sales, COUNT(*) AS Total_Transactions FROM sales_orders GROUP BY Payment_Mode ORDER BY Total_Sales DESC;
