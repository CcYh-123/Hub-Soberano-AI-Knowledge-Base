-- 1. Table Setup ensure user_id exists
ALTER TABLE IF EXISTS public.parcelas ADD COLUMN IF NOT EXISTS user_id UUID DEFAULT auth.uid();
ALTER TABLE IF EXISTS public.movimientos_stock ADD COLUMN IF NOT EXISTS user_id UUID DEFAULT auth.uid();
ALTER TABLE IF EXISTS public.insumos_stock ADD COLUMN IF NOT EXISTS user_id UUID DEFAULT auth.uid();

-- 2. Enable RLS
ALTER TABLE public.parcelas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.movimientos_stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insumos_stock ENABLE ROW LEVEL SECURITY;

-- 3. RLS Policies: auth.uid() = user_id
DO $$ 
BEGIN
    DROP POLICY IF EXISTS "Individual user access" ON public.parcelas;
    DROP POLICY IF EXISTS "Individual user access" ON public.movimientos_stock;
    DROP POLICY IF EXISTS "Individual user access" ON public.insumos_stock;
END $$;

CREATE POLICY "Individual user access" ON public.parcelas
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Individual user access" ON public.movimientos_stock
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Individual user access" ON public.insumos_stock
  FOR ALL USING (auth.uid() = user_id);

-- 4. Automatic Auditing Trigger Function
CREATE OR REPLACE FUNCTION public.set_user_id()
RETURNS trigger AS $$
BEGIN
  IF new.user_id IS NULL THEN
    new.user_id := auth.uid();
  END IF;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Create Triggers
DROP TRIGGER IF EXISTS tr_set_user_id_parcelas ON public.parcelas;
CREATE TRIGGER tr_set_user_id_parcelas
  BEFORE INSERT ON public.parcelas
  FOR EACH ROW EXECUTE PROCEDURE public.set_user_id();

DROP TRIGGER IF EXISTS tr_set_user_id_movimientos ON public.movimientos_stock;
CREATE TRIGGER tr_set_user_id_movimientos
  BEFORE INSERT ON public.movimientos_stock
  FOR EACH ROW EXECUTE PROCEDURE public.set_user_id();

DROP TRIGGER IF EXISTS tr_set_user_id_insumos ON public.insumos_stock;
CREATE TRIGGER tr_set_user_id_insumos
  BEFORE INSERT ON public.insumos_stock
  FOR EACH ROW EXECUTE PROCEDURE public.set_user_id();
