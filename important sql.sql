-- parse date from file name

SELECT
	DISTINCT 
	STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d')
FROM
	credit_card_transaction_files cctf
where
	Transaction_Date is not null;

-- replacing month apprev with number

SELECT
distinct value_date , CASE
        WHEN value_date LIKE '%Jan%' THEN REPLACE(value_date, 'Jan', '01')
        WHEN value_date LIKE '%Feb%' THEN REPLACE(value_date, 'Feb', '02')
        WHEN value_date LIKE '%Mar%' THEN REPLACE(value_date, 'Mar', '03')
        WHEN value_date LIKE '%Apr%' THEN REPLACE(value_date, 'Apr', '04')
        WHEN value_date LIKE '%May%' THEN REPLACE(value_date, 'May', '05')
        WHEN value_date LIKE '%Jun%' THEN REPLACE(value_date, 'Jun', '06')
        WHEN value_date LIKE '%Jul%' THEN REPLACE(value_date, 'Jul', '07')
        WHEN value_date LIKE '%Aug%' THEN REPLACE(value_date, 'Aug', '08')
        WHEN value_date LIKE '%Sep%' THEN REPLACE(value_date, 'Sep', '09')
        WHEN value_date LIKE '%Oct%' THEN REPLACE(value_date, 'Oct', '10')
        WHEN value_date LIKE '%Nov%' THEN REPLACE(value_date, 'Nov', '11')
        WHEN value_date LIKE '%Dec%' THEN REPLACE(value_date, 'Dec', '12')
        ELSE value_date
    END AS updated_value_date
FROM
	credit_card_transaction_files cctf;



-- extracted the card_type,formated dates  
SELECT
	str_to_date(CONCAT(Transaction_Date, '-', DATE_FORMAT(STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d'), '%Y') ),
	'%d-%m-%Y') as updated_transaction_date ,
	str_to_date(CONCAT(Value_Date , '-', DATE_FORMAT(STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d'), '%Y') ),
	'%d-%m-%Y') as updated_value_date ,
	Description ,
	signed_amount ,
	STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d') as statement_date,
	trim(REGEXP_SUBSTR(file_name, '[a-z]+[A-Z]+')) as card_type
FROM
	credit_card_transaction_files cctf

-- summary

with summary as (
select
	last_day(STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d')) as statement_date,
	sum(DISTINCT card_limit) as total_credit_limit,
	sum(DISTINCT Available_Credit_Limit) Available_Credit_Limit ,
	sum(Total_Amount_Due) Total_Amount_Due
from
	credit_card_transaction_summary ccts
group by
	last_day(STR_TO_DATE(CONCAT(REGEXP_SUBSTR(file_name, '[0-9]+'), '01') ,
	'%Y%m%d'))
)select
	statement_date,
	total_credit_limit,
	LAG (total_credit_limit,
	1,
	0)over(
	order by statement_date asc) as prev_month_total_credit_limit,
	available_credit_limit,
	LAG (available_credit_limit,
	1,
	0)over(
	order by statement_date asc) prev_month_available_credit,
	total_amount_due,LAG (total_amount_due,
	1,
	0)over(
	order by statement_date asc) prev_month_total_amount_due
from
	summary
order by
	statement_date ASC ;
	

-- TRUNCATE  credit_card_transaction_files 