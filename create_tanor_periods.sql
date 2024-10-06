create view Tenor_Periods as 
with get_payment_due_date as(
select
	Type_of_Credit_Card,
	file_name,
	CASE
		when Payment_Due_Date like '%/%/%' then STR_TO_DATE(Payment_Due_Date ,
		'%d/%m/%y')
		when Payment_Due_Date like '%-%-%' then STR_TO_DATE(Payment_Due_Date ,
		'%Y-%m-%d')
	END Payment_Due_Date
from
	credit_card_transaction_summary ccts ),
	get_potential_tenor_start_date as (
select
	type_of_credit_card,
	file_name,
	DATE_SUB(Payment_due_date, INTERVAL 55 DAY) potential_tenor_start_date
from
	get_payment_due_date),
	get_most_freuqancy_of_day_of_month as (
select
	type_of_credit_Card,
	day(potential_tenor_start_date) as day_of_month,
	count(1) as counter
from
	get_potential_tenor_start_date
group by
	type_of_credit_Card,
	day(potential_tenor_start_date)),
	rank_the_frequancy_day as (
SELECT
	type_of_credit_card,
	day_of_month,
	dense_rank() over(PARTITION by type_of_credit_card
order by
	counter desc) the_rank
from
	get_most_freuqancy_of_day_of_month),
get_most_frequant_day as(
select
	type_of_credit_Card,
	day_of_month
from
	rank_the_frequancy_day
where
	the_rank = 1
),
get_tenor_start_date as(
select
	file_name,
	CASE 
		when abs(day(potential_tenor_start_date)-day_of_month) <5 then date_sub(potential_tenor_start_date, interval day(potential_tenor_start_date)-day_of_month day)
		when abs(day(potential_tenor_start_date)-day_of_month) > 25 then date_add(LAST_DAY(potential_tenor_start_date), interval day_of_month day)
	END tenor_start_date
from
	get_potential_tenor_start_date
inner join get_most_frequant_day on
	get_most_frequant_day.type_of_credit_Card = get_potential_tenor_start_date.type_of_credit_Card)
select
	gpdd.type_of_credit_card,gpdd.file_name,gtsd.tenor_StarT_date,gpdd.payment_due_date
from
	get_tenor_start_date gtsd inner join get_payment_due_date gpdd on gtsd.file_name=gpdd.file_name
    