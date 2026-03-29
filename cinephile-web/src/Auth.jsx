import React, { useState } from 'react';
import { supabase } from './supabaseClient';


export default function Auth({ onLogin }) {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isSignUp) {
        // Create a brand new user
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        alert("Success! Welcome to CineMatch.");
        if (data.user) onLogin(data.user);
      } else {
        // Log in an existing user
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        if (data.user) onLogin(data.user);
      }
    } catch (error) {
      alert(error.message); // Show them if they typed the wrong password!
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container fade-in">
      <div className="auth-card">
        <h2 className="auth-title">{isSignUp ? "Create an Account" : "Welcome Back"}</h2>
        <p className="auth-subtitle">
          {isSignUp ? "Join the cinematic universe." : "Log in to access your personal vault."}
        </p>

        <form onSubmit={handleAuth} className="auth-form">
          <input
            className="auth-input"
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="auth-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button className="large-gradient-btn auth-submit-btn" disabled={loading}>
            {loading ? "Processing..." : isSignUp ? "Sign Up" : "Log In"}
          </button>
        </form>

        <button className="auth-switch-btn" onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp ? "Already have an account? Log In" : "Need an account? Sign Up"}
        </button>
      </div>
    </div>
  );
}