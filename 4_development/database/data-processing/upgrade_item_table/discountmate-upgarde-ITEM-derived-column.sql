create table TEMP_ITEM_NEW select * from ITEM;


alter table TEMP_ITEM_NEW add column ITEM_MEASUREMENT decimal(6,2);
alter table TEMP_ITEM_NEW add column ITEM_MEASUREMENT_UNIT varchar(255);
alter table TEMP_ITEM_NEW add column ITEM_UNIT varchar(255);
alter table TEMP_ITEM_NEW add column ITEM_UNIT_PRICE decimal(6,2);


-- Update derived data into ITEM_UNIT column
update TEMP_ITEM_NEW 
set ITEM_UNIT = substring(ITEM_DESC, position('/' in ITEM_DESC)+2, length(ITEM_DESC))
where substring(ITEM_DESC, 2, position('/' in ITEM_DESC)-2) <> ''
;


update TEMP_ITEM_NEW 
set ITEM_UNIT_PRICE = substring(ITEM_DESC, position('per' in ITEM_DESC)+2, length(ITEM_DESC))
where ITEM_DESC like '%per%'
;


-- Update derived data into ITEM_UNIT_PRICE column
update TEMP_ITEM_NEW 
set ITEM_UNIT_PRICE = CAST(substring(ITEM_DESC, 2, position('/' in ITEM_DESC)-2)AS DECIMAL(6,2))
where substring(ITEM_DESC, 2, position('/' in ITEM_DESC)-2) <> ''
;


update TEMP_ITEM_NEW 
set ITEM_UNIT_PRICE = CAST(substring(ITEM_DESC, 2, position('per' in ITEM_DESC)-2)AS DECIMAL(6,2))
where ITEM_DESC like '%per%'
;


-- Update ITEM_MEASUREMENT and ITEM_MEASUREMENT_UNIT type by type
Update TEMP_ITEM_NEW 
set 
ITEM_MEASUREMENT = 100,
ITEM_MEASUREMENT_UNIT = 'ea'
where ITEM_UNIT = '100 each'
;


Update TEMP_ITEM_NEW 
set 
ITEM_MEASUREMENT = 10,
ITEM_MEASUREMENT_UNIT = 'g'
where ITEM_UNIT = '10g'
;


-- After confirmed data correctness and backup ITEM table, rename TEMP_ITEM_NEW to ITEM table 
ALTER TABLE TEMP_ITEM_NEW RENAME ITEM;