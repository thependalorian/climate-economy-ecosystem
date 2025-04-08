import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import supabase from '@/lib/supabase-client';

/**
 * Next-Auth API Route
 * Handles authentication using App Router
 * Location: /app/api/auth/[...nextauth]/route.js
 */

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      profile(profile) {
        return {
          id: profile.sub,
          email: profile.email,
          name: profile.name,
          image: profile.picture,
          role: 'user',
        };
      },
    }),
    CredentialsProvider({
      name: 'Email and Password',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email: credentials.email,
            password: credentials.password,
          });

          if (error || !data.user) {
            console.error('Authentication error:', error);
            return null;
          }

          // Get user profile from database
          const { data: profileData } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', data.user.id)
            .single();

          // Return user with profile data
          return {
            id: data.user.id,
            email: data.user.email,
            name: profileData?.full_name || data.user.email,
            role: profileData?.role || 'user',
            image: profileData?.avatar_url,
            profile: profileData || {},
          };
        } catch (error) {
          console.error('Authorization error:', error);
          return null;
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    // Handle sign in
    async signIn({ user, account, profile }) {
      // Only handle Google sign-in here
      if (account.provider === 'google') {
        try {
          // Check if user exists in Supabase
          const { data: existingUser, error: userError } = await supabase
            .from('profiles')
            .select('*')
            .eq('email', user.email)
            .single();

          if (userError && !userError.message.includes('No rows found')) {
            console.error('Error checking for existing user:', userError);
            return false;
          }

          // If user doesn't exist, create a new one
          if (!existingUser) {
            // Create user in Supabase Auth
            const { data: authData, error: authError } = await supabase.auth.admin.createUser({
              email: user.email,
              email_confirm: true,
              user_metadata: {
                full_name: user.name,
                avatar_url: user.image,
                provider: 'google',
              },
            });

            if (authError) {
              console.error('Error creating user in Supabase Auth:', authError);
              return false;
            }

            // Create user profile
            const { error: profileError } = await supabase
              .from('profiles')
              .insert({
                id: authData.user.id,
                email: user.email,
                full_name: user.name,
                avatar_url: user.image,
                role: 'user',
              });

            if (profileError) {
              console.error('Error creating user profile:', profileError);
              return false;
            }
          }

          return true;
        } catch (error) {
          console.error('Error in Google sign-in:', error);
          return false;
        }
      }

      return true;
    },
    // Include user data in the JWT token
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
        token.role = user.role;
        token.profile = user.profile;

        // Add provider information
        if (account) {
          token.provider = account.provider;
        }
      }
      return token;
    },
    // Make user data available in the session
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id;
        session.user.role = token.role;
        session.user.profile = token.profile;
        session.user.provider = token.provider;
      }
      return session;
    }
  },
  pages: {
    signIn: '/login',
    signOut: '/',
    error: '/error',
  },
  debug: process.env.NODE_ENV === 'development',
});

export { handler as GET, handler as POST };