
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select invoice_number
from "docstream"."main"."stg_invoices"
where invoice_number is null



  
  
      
    ) dbt_internal_test