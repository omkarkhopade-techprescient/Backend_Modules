-- https://www.geeksforgeeks.org/sql-interview-questions-set-1/

-- SQL Interview Questions | Set 1
-- Last Updated : 11 Jul, 2025

-- Que-1:

-- Difference between blocking and deadlocking: 
-- Blocking: Blocking occurs is a transaction tries to acquire an incompatible lock on a resource that another transaction has already locked. The blocked transaction remain blocked until the blocking transaction releases the lock.
-- Deadlocking: Deadlocking occurs when two or more transactions have a resource locked, and each transaction requests a lock on the resource that another transaction has already locked. Neither of the transactions here can more forward, as each one is waiting for the other to release the lock.

-- Que-2:

-- Delete duplicate data from table only first data remains constant.

-- Managers -

-- Id	Name	    Salary
-- 1	Harpreet	20000
-- 2	Ravi	    30000
-- 3	Vinay	    10000
-- 4	Ravi	    30000
-- 5	Harpreet    20000
-- 6	Vinay	    10000
-- 7	Rajeev	    40000
-- 8	Vinay	    10000
-- 9	Ravi	    30000
-- 10	Sanjay	    50000

-- Query -

DELETE M1 
From managers M1, managers M2 
Where M2.Name = M1.Name AND M1.Id>M2.Id; 

-- Output -

-- Id	Name	Salary
-- 1	Harpreet	20000
-- 2	Ravi	30000
-- 3	Vinay	10000
-- 7	Rajeev	40000
-- 10	Sanjay	50000

-- Que-3:

-- Find the Name of Employees. Finding the name of Employees where First Name, Second Name and Last Name is given in table. Some Name is missing such as First Name, Second Name and may be Last Name. Here we will use COALESCE() function which will return first Non Null values.

-- Employees -

-- ID	FName	SName	LName	Salary
-- 1	Har	preet	Singh	30000
-- 2	Ashu	NULL	Rana	50000
-- 3	NULL	Vinay	Thakur	40000
-- 4	NULL	Vinay	NULL	10000
-- 5	NULL	NULL	Rajveer	60000
-- 6	Manjeet	Singh	NULL	60000

-- Query -

SELECT ID, COALESCE(FName, SName, LName) as Name 
FROM employees; 

-- Output -

-- Que-4:

-- Find the Employees who hired in the Last n months. Finding the Employees who have been hire in the last n months. Here we get desire output by using TIMESTAMPDIFF() mysql function.

-- Employees -

-- ID	FName	LName	Gender	Salary	Hiredate
-- 1	Rajveer	Singh	Male	30000	2017/11/05
-- 2	Manveer	Singh	Male	50000	2017/11/05
-- 3	Ashutosh Kumar	Male	40000	2017/12/12
-- 4	Ankita	Sharma	Female	45000	2017/12/15
-- 5	Vijay	Kumar	Male	50000	2018/01/12
-- 6	Dilip	Yadav	Male	25000	2018/02/26
-- 7	Jayvijay Singh	Male	30000	2018/02/18
-- 8	Reenu	Kumari	Female	40000	2017/09/19
-- 9	Ankit	Verma	Male	25000	2018/04/04
-- 10	Harpreet Singh	Male	50000	2017/10/10

-- Query -

Select *, TIMESTAMPDIFF (month, Hiredate, current_date()) as DiffMonth 
From employees
Where TIMESTAMPDIFF (month, Hiredate, current_date()) 
Between 1 and 5 Order by Hiredate desc; 

-- Note -

-- Here in query 1 and 5 are indicates 1 to n months.which show the Employees who have hired last 1 to 5 months. In this query DiffMonth is a extra column for our understanding which show the Nth months.

-- Output -


-- Que-5:

-- Find the Employees who hired in the Last n days. Finding the Employees who have been hire in the last n days. Here we get desire output by using DATEDIFF() mysql function.

-- Employees -

-- ID	FName	LName	Gender	Salary	Hiredate
-- 1	Rajveer	Singh	Male	30000	2017/11/05
-- 2	Manveer	Singh	Male	50000	2017/11/05
-- 3	Ashutosh Kumar	Male	40000	2017/12/12
-- 4	Ankita	Sharma	Female	45000	2017/12/15
-- 5	Vijay	Kumar	Male	50000	2018/01/12
-- 6	Dilip	Yadav	Male	25000	2018/02/26
-- 7	Jayvijay Singh	Male	30000	2018/02/18
-- 8	Reenu	Kumari	Female	40000	2017/09/19
-- 9	Ankit	Verma	Male	25000	2018/04/04
-- 10	Harpreet Singh	Male	50000	2017/10/10

-- Query -

Select *, DATEDIFF (current_date(), Hiredate) as DiffDay 
From employees
Where DATEDIFF (current_date(), Hiredate) between 1 and 100 order by Hiredate desc;
 
-- Note -

-- Here in query 1 and 100 are indicates 1 to n days.which show the Employees who have hired last 1 to 100 days. In this query DiffDay is a extra column for our understanding which show the Nth days.

-- Output -

-- Que-6:

-- Find the Employees who hired in the Last n years. Finding the Employees who have been hire in the last n years. Here we get desire output by using TIMESTAMPDIFF() mysql function.

-- Employees -

-- ID	FName	LName	Gender	Salary	Hiredate
-- 1	Rajveer	Singh	Male	30000	2010/11/05
-- 2	Manveer	Singh	Male	50000	2017/11/05
-- 3	Ashutosh Kumar	Male	40000	2015/12/12
-- 4	Ankita	Sharma	Female	45000	2016/12/15
-- 5	Vijay	Kumar	Male	50000	2017/01/12
-- 6	Dilip	Yadav	Male	25000	2011/02/26
-- 7	Jayvijay Singh	Male	30000	2012/02/18
-- 8	Reenu	Kumari	Female	40000	2013/09/19
-- 9	Ankit	Verma	Male	25000	2017/04/04
-- 10	Harpreet Singh	Male	50000	2017/10/10

-- Query -

Select *, TIMESTAMPDIFF (year, Hiredate, current_date()) as DiffYear 
From employees
Where TIMESTAMPDIFF (year, Hiredate, current_date()) between 1 and 4 order by Hiredate desc; 

-- Note -

-- Here in query 1 and 4 are indicates 1 to n years.which show the Employees who have hired last 1 to 4 years. In this query DiffYear is a extra column for our understanding which show the Nth years.

-- Output -

-- Que-7:

-- Select all names that start with a given letter. Here we get desire output by using three different query.

-- Employees -

-- ID	FName	LName	Gender	Salary	Hiredate
-- 1	Rajveer	Singh	Male	30000	2010/11/05
-- 2	Manveer	Singh	Male	50000	2017/11/05
-- 3	Ashutosh	Kumar	Male	40000	2015/12/12
-- 4	Ankita	Sharma	Female	45000	2016/12/15
-- 5	Vijay	Kumar	Male	50000	2017/01/12
-- 6	Dilip	Yadav	Male	25000	2011/02/26
-- 7	Jayvijay	Singh	Male	30000	2012/02/18
-- 8	Reenu	Kumari	Female	40000	2013/09/19
-- 9	Ankit	Verma	Male	25000	2017/04/04
-- 10	Harpreet	Singh	Male	50000	2017/10/10

-- Query -

Select *
From employees 
Where Fname like 'A%';

Select *
From employees 
Where left(FName, 1)='A';

Select *
From employees 
Where substring(FName, 1, 1)='A';