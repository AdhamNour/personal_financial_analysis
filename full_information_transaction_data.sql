with due_dates as (
select
	case
		when Payment_Due_Date like '%/%/%' then STR_TO_DATE(Payment_Due_Date,
		'%d/%m/%y')
		when payment_Due_Date like '%-%-%' then STR_TO_DATE(Payment_Due_Date,
		'%Y-%m-%d')
	end Payment_Due_Date,
	file_name,
	Type_of_Credit_Card
from
	credit_card_transaction_summary ccts)
select
		case
		when str_to_date(CONCAT(cctf.Value_Date , '-', DATE_FORMAT(DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY), '%Y') ),
		'%d-%m-%Y') between DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY) and dd.Payment_Due_Date then str_to_date(CONCAT(cctf.Value_Date , '-', DATE_FORMAT(DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY), '%Y') ),
		'%d-%m-%Y')
		else str_to_date(CONCAT(cctf.Value_Date , '-', DATE_FORMAT(dd.Payment_Due_Date, '%Y') ),
		'%d-%m-%Y')
	end updated_value_date,
	case
		when str_to_date(CONCAT(cctf.Transaction_Date , '-', DATE_FORMAT(DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY), '%Y') ),
		'%d-%m-%Y') between DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY) and dd.Payment_Due_Date then str_to_date(CONCAT(cctf.Value_Date , '-', DATE_FORMAT(DATE_SUB(dd.Payment_Due_Date, INTERVAL 55 DAY), '%Y') ),
		'%d-%m-%Y')
		else str_to_date(CONCAT(cctf.Transaction_Date , '-', DATE_FORMAT(dd.Payment_Due_Date, '%Y') ),
		'%d-%m-%Y')
	end updated_transaction_date,
	Description ,
	signed_amount ,
	dd.Type_of_Credit_Card
from
	credit_card_transaction_files cctf
left outer join due_dates dd on
	cctf.file_name = dd.file_name
