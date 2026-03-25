import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.VITE_SUPABASE_URL || 'https://ijzazwdgtxsosiibjoj.supabase.co'
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_Isfp5ej3p9oq26bZpiYGEA_sNeop1Fd'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
