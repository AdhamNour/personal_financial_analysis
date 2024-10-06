create view  all_installments as
with tenor_periods_1 as(
select
	tp.tenor_StarT_date AS tenor_start_date,
	cast(greatest(lag(tp.tenor_StarT_date, 1, 0) OVER (PARTITION BY tp.type_of_credit_card ORDER BY tp.tenor_StarT_date ) , min(tp.tenor_StarT_date) OVER (PARTITION BY tp.type_of_credit_card ORDER BY tp.tenor_StarT_date ) ) as date) AS prev_tenor_date,
	tp.payment_due_date AS Payment_Due_Date,
	cast(greatest(lag(tp.payment_due_date, 1, 0) OVER (PARTITION BY tp.type_of_credit_card ORDER BY tp.payment_due_date ) , min(tp.payment_due_date) OVER (PARTITION BY tp.type_of_credit_card ORDER BY tp.payment_due_date ) ) as date) AS prev_payment_due_date,
	tp.type_of_credit_card AS type_of_credit_card,
	tp.file_name AS file_name
from
	tenor_periods tp
),
GET_ENROLLMENT_DATE AS(
select
	ccis.Marchant_Name,
	(case
		when (str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.tenor_start_date, '%Y')),
		'%d-%m-%Y') between tp.tenor_start_date and tp.Payment_Due_Date) then str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.tenor_start_date, '%Y')),
		'%d-%m-%Y')
		when (str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.Payment_Due_Date, '%Y')),
		'%d-%m-%Y') between tp.tenor_start_date and tp.Payment_Due_Date) then str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.Payment_Due_Date, '%Y')),
		'%d-%m-%Y')
		when (str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.prev_tenor_date, '%Y')),
		'%d-%m-%Y') between tp.prev_tenor_date and tp.prev_payment_due_date) then str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.prev_tenor_date, '%Y')),
		'%d-%m-%Y')
		when (str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.prev_payment_due_date, '%Y')),
		'%d-%m-%Y') between tp.prev_tenor_date and tp.prev_payment_due_date) then str_to_date(concat(REPLACE(ccis.Enrollment_Date, '/', '-'), '-', date_format(tp.prev_payment_due_date, '%Y')),
		'%d-%m-%Y')
	end) AS Enrollment_Date ,
	ccis.Total_Number_Of_Installments,
	REPLACE(ccis.Enrollment_Date, '/', '-') as key_enrollment_date
from
	credit_card_installments_summary ccis
inner join tenor_periods_1 tp on
	ccis.file_name = tp.file_name
	and ccis.Installment_No = 1)
select
	ccis.Marchant_Name,
	ged.enrollment_date,
	ccis.Principle,
	ccis.interest,
	ccis.total,
	ccis.Installment_No,
	ccis.Total_Number_Of_Installments,ccis.file_name
from
	credit_card_installments_summary ccis
inner join GET_ENROLLMENT_DATE GED on
	ccis.Marchant_Name = ged.Marchant_Name
	and ccis.Total_Number_Of_Installments = ged.Total_Number_Of_Installments
	and REPLACE(ccis.Enrollment_Date, '/', '-')= key_enrollment_date
	
	;