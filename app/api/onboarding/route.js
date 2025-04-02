import { createServerSupabaseClient } from '@/lib/supabase'
import { NextResponse } from 'next/server'

export async function POST(req) {
  try {
    const supabase = createServerSupabaseClient()
    
    // Get the current user's session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    if (sessionError || !session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Get the onboarding data from the request
    const onboardingData = await req.json()
    
    // Update the user's profile in Supabase
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .upsert({
        id: session.user.id,
        email: session.user.email,
        full_name: `${onboardingData.firstName} ${onboardingData.lastName}`,
        persona: onboardingData.persona,
        skills: onboardingData.skills,
        interests: onboardingData.interests,
        location: onboardingData.location,
        background: onboardingData.background,
        will_relocate: onboardingData.willRelocate,
        in_ej_community: onboardingData.inEJCommunity,
        consent_to_share: onboardingData.consentToShare,
        consent_to_email: onboardingData.consentToEmail,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .select()
      .single()

    if (profileError) {
      console.error('Error updating profile:', profileError)
      return NextResponse.json(
        { error: 'Failed to update profile' },
        { status: 500 }
      )
    }

    return NextResponse.json({ profile })
  } catch (error) {
    console.error('Onboarding error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 