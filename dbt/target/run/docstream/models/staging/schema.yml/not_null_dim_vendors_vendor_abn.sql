
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select vendor_abn
from "docstream"."main"."dim_vendors"
where vendor_abn is null



  
  
      
    ) dbt_internal_test