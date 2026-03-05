"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/utils/supabase/client"
import { useRouter } from "next/navigation"

export function AuthGate({ children }: { children: React.ReactNode }) {
    const [loading, setLoading] = useState(true)
    const [session, setSession] = useState<any>(null)
    const router = useRouter()
    const supabase = createClient()

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setLoading(false)
            if (!session) {
                router.push("/login")
            }
        })

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            if (!session) {
                router.push("/login")
            }
        })

        return () => subscription.unsubscribe()
    }, [router, supabase])

    if (loading) {
        return (
            <div className="h-screen w-screen bg-slate-50 flex flex-col items-center justify-center">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-slate-500 text-sm font-medium animate-pulse">Autenticando sesión...</p>
            </div>
        )
    }

    return session ? <>{children}</> : null
}
