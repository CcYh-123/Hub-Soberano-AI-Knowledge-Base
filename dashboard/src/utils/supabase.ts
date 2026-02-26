import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ijzazdwdgtxsosiibjoj.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqemF6ZHdkZ3R4c29zaWliam9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNjMyMTIsImV4cCI6MjA4NzYzOTIxMn0.NVQpQFJlfHC1eKWSenc9XfMfRyeJ6W0OCkKzZqXN1lQ'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
