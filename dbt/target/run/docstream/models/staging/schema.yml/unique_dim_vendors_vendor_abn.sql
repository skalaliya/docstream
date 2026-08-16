
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    vendor_abn as unique_field,
    count(*) as n_records

from "docstream"."main"."dim_vendors"
where vendor_abn is not null
group by vendor_abn
having count(*) > 1



  
  
      
    ) dbt_internal_test