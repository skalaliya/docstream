
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select source_sha256
from "docstream"."main"."stg_invoices"
where source_sha256 is null



  
  
      
    ) dbt_internal_test