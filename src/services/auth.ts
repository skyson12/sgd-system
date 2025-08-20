import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'http://localhost:3001'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

interface LoginResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    isActive: boolean;
  };
}

export class AuthService {
  static async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        throw new Error(error.message)
      }

      if (!data.user || !data.session) {
        throw new Error('Login failed')
      }

      return {
        token: data.session.access_token,
        user: {
          id: data.user.id,
          username: data.user.email?.split('@')[0] || 'user',
          email: data.user.email || '',
          firstName: data.user.user_metadata?.first_name,
          lastName: data.user.user_metadata?.last_name,
          isActive: true
        }
      }
    } catch (error) {
      throw new Error('Authentication failed')
    }
  }

  static async signUp(email: string, password: string, firstName?: string, lastName?: string): Promise<void> {
    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            first_name: firstName,
            last_name: lastName,
          }
        }
      })

      if (error) {
        throw new Error(error.message)
      }
    } catch (error) {
      throw new Error('Sign up failed')
    }
  }

  static async getCurrentUser(token: string) {
    try {
      const { data: { user }, error } = await supabase.auth.getUser(token)

      if (error || !user) {
        throw new Error('Failed to get user info')
      }

      return {
        id: user.id,
        username: user.email?.split('@')[0] || 'user',
        email: user.email || '',
        firstName: user.user_metadata?.first_name,
        lastName: user.user_metadata?.last_name,
        isActive: true
      }
    } catch (error) {
      throw error
    }
  }

  static async logout() {
    await supabase.auth.signOut()
    localStorage.removeItem('sgd_token')
  }

  static async resetPassword(email: string) {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      })

      if (error) {
        throw new Error(error.message)
      }
    } catch (error) {
      throw new Error('Password reset failed')
    }
  }
}