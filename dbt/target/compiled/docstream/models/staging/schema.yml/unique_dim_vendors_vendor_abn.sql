
    
    

select
    vendor_abn as unique_field,
    count(*) as n_records

from "docstream"."main"."dim_vendors"
where vendor_abn is not null
group by vendor_abn
having count(*) > 1


