
    

    create  table
      "docstream"."main"."fct_monthly_spend__dbt_tmp"
  
    
    as (
      -- Monthly spend fact table
select
    date_trunc('month', invoice_date)   as spend_month,
    currency,
    count(*)                            as invoice_count,
    sum(total_amount)                   as total_spend,
    avg(total_amount)                   as avg_invoice_amount
from "docstream"."main"."stg_invoices"
group by 1, 2
order by 1
    );
    
  