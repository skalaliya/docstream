-- Staging: typed view over the silver invoice parquet
select
    source_sha256,
    invoice_number,
    cast(invoice_date as date)          as invoice_date,
    coalesce(vendor_abn, 'UNKNOWN')     as vendor_abn,
    cast(total_amount as decimal(12,2)) as total_amount,
    coalesce(currency, 'AUD')           as currency
from '../data/silver/invoices.parquet'