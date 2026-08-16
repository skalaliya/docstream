
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_amount
from "docstream"."main"."stg_invoices"
where total_amount is null



  
  
      
    ) dbt_internal_test