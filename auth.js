import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import supabase from '@/lib/supabase-client';

/**
 * Next-Auth Configuration
 * Shared configuration for Next-Auth
 * Location: /auth.js
 */

export const authConfig = {
  providers: [
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
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          role: 'user',
        };
      },
    }),
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    // Include user data in the JWT token
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
        token.role = user.role;
        token.profile = user.profile;
      }
      
      // If sign in with OAuth
      if (account && account.provider === 'google') {
        // Check if user exists or create a new profile
        const { data: existingUser } = await supabase
          .from('profiles')
          .select('*')
          .eq('email', token.email)
          .single();
        
        if (!existingUser) {
          // Create new profile
          const { data: newProfile } = await supabase
            .from('profiles')
            .insert({
              id: token.sub,
              email: token.email,
              full_name: token.name,
              avatar_url: token.picture,
              role: 'user',
            })
            .select()
            .single();
            
          token.profile = newProfile || {};
        } else {
          token.profile = existingUser;
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
      }
      return session;
    }
  },
  pages: {
    signIn: '/auth/signin',
    signOut: '/',
    error: '/error',
  },
  debug: process.env.NODE_ENV === 'development',
};

export default NextAuth(authConfig); 