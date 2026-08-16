
    
    

select
    source_sha256 as unique_field,
    count(*) as n_records

from "docstream"."main"."stg_invoices"
where source_sha256 is not null
group by source_sha256
having count(*) > 1


