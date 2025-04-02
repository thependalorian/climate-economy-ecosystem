import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const authOptions = {
  // Configure authentication providers
  providers: [
    // Username/password authentication
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email", placeholder: "your@email.com" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        try {
          // Sign in with Supabase Auth
          const { data, error } = await supabase.auth.signInWithPassword({
            email: credentials.email,
            password: credentials.password,
          });

          if (error) {
            console.error("Supabase authentication error:", error.message);
            return null;
          }

          // Return user data
          return {
            id: data.user.id,
            email: data.user.email,
            name: data.user.user_metadata?.name || data.user.email,
            accessToken: data.session.access_token,
            refreshToken: data.session.refresh_token,
          };
        } catch (error) {
          console.error("Authentication error:", error);
          return null;
        }
      },
    }),
    
    // Google OAuth authentication
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      allowDangerousEmailAccountLinking: true, // Allow linking with existing accounts
    }),
  ],
  
  // Database session management
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  
  // JWT configuration
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
  },
  
  // Callbacks
  callbacks: {
    // Add user information to the session
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub;
        session.user.accessToken = token.accessToken;
        session.user.refreshToken = token.refreshToken;
      }
      return session;
    },
    
    // JWT callback to store tokens
    async jwt({ token, user, account }) {
      // Initial sign in
      if (account && user) {
        return {
          ...token,
          accessToken: user.accessToken || account.access_token,
          refreshToken: user.refreshToken || account.refresh_token,
          accessTokenExpires: account.expires_at ? account.expires_at * 1000 : null,
        };
      }

      // Return previous token if the access token has not expired yet
      if (token.accessTokenExpires && Date.now() < token.accessTokenExpires) {
        return token;
      }

      // Access token has expired, try to refresh
      try {
        const { data, error } = await supabase.auth.refreshSession({
          refresh_token: token.refreshToken,
        });

        if (error) {
          throw error;
        }

        return {
          ...token,
          accessToken: data.session.access_token,
          refreshToken: data.session.refresh_token,
          accessTokenExpires: Date.now() + 60 * 60 * 1000, // 1 hour
        };
      } catch (error) {
        console.error("Token refresh error:", error);
        return { ...token, error: "RefreshAccessTokenError" };
      }
    },
    
    // Handle sign in callback
    async signIn({ user, account, profile }) {
      // Handle Google OAuth sign in
      if (account.provider === "google") {
        try {
          // Check if this user exists in Supabase
          const { data: existingUser, error: checkError } = await supabase
            .from("user_profiles")
            .select("*")
            .eq("email", user.email)
            .single();

          // Create user profile if doesn't exist
          if (checkError || !existingUser) {
            const { data, error } = await supabase
              .from("user_profiles")
              .insert({
                user_id: user.id,
                name: user.name,
                email: user.email,
                preferences: {},
              });

            if (error) {
              console.error("Error creating user profile:", error);
            }
          }
        } catch (error) {
          console.error("Error during Google sign in:", error);
        }
      }
      
      return true;
    },
  },
  
  // Pages
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signout",
    error: "/auth/error",
  },
  
  // Debug mode - set to true only in development
  debug: process.env.NODE_ENV === "development",
};

// Export handler
export default NextAuth(authOptions); 