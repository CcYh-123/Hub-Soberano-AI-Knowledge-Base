-- CLEANUP SCRIPT: Run this before production handover
-- WARNING: This will delete ALL data in the specified tables.

BEGIN;

-- Disable triggers temporarily if necessary
-- ALTER TABLE public.parcelas DISABLE TRIGGER ALL;

TRUNCATE TABLE 
    public.aplicaciones, 
    public.movimientos_stock, 
    public.parcelas,
    public.insumos_stock
RESTART IDENTITY CASCADE;

-- ALTER TABLE public.parcelas ENABLE TRIGGER ALL;

COMMIT;

-- Verification query
SELECT 'Cleanup complete. Total parcelas: ' || count(*) FROM public.parcelas;
