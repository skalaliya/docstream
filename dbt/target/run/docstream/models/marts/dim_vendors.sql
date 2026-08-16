
    

    create  table
      "docstream"."main"."dim_vendors__dbt_tmp"
  
    
    as (
      -- One row per vendor (by ABN), with lifetime stats
select
    vendor_abn,
    count(*)                        as invoice_count,
    sum(total_amount)               as lifetime_spend,
    min(invoice_date)               as first_invoice_date,
    max(invoice_date)               as last_invoice_date
from "docstream"."main"."stg_invoices"
group by 1
    );
    
  